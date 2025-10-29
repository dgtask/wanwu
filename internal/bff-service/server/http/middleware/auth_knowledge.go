package middleware

import (
	"bytes"
	"encoding/json"
	"errors"
	"github.com/UnicomAI/wanwu/internal/bff-service/service"
	gin_util "github.com/UnicomAI/wanwu/pkg/gin-util"
	"github.com/UnicomAI/wanwu/pkg/log"
	"github.com/gin-gonic/gin"
	"github.com/gin-gonic/gin/binding"
	"io"
	"net/http"
)

const (
	KnowledgeView   int32 = 0
	KnowledgeEdit   int32 = 10
	KnowledgeGrant  int32 = 20
	KnowledgeSystem int32 = 30
)

// AuthKnowledgeDoc 校验知识库权限
func AuthKnowledgeDoc(fieldName string, permissionType int32) func(ctx *gin.Context) {
	return func(ctx *gin.Context) {
		defer func() {
			if err := recover(); err != nil {
				log.Errorf("SensitiveCheck panic: %v", err)
			}
		}()
		//1.获取value值
		value := GetFieldValue(ctx, fieldName)
		if len(value) == 0 {
			gin_util.ResponseErrWithStatus(ctx, http.StatusBadRequest, errors.New("docId is required"))
			ctx.Abort()
			return
		}
		//2.根据docId获取知识库id
		knowledgeId, err := searchKnowledgeId(ctx, value)
		if err != nil {
			gin_util.ResponseErrWithStatus(ctx, http.StatusBadRequest, err)
			ctx.Abort()
			return
		}
		//3.校验用户授权权限
		err = knowledgeGrantUser(ctx, knowledgeId, permissionType)
		//4.异常处理
		if err != nil {
			gin_util.ResponseErrWithStatus(ctx, http.StatusBadRequest, err)
			ctx.Abort()
			return
		}
	}
}

// AuthKnowledgeIfHas 校验知识库权限,允许字段为空
func AuthKnowledgeIfHas(fieldName string, permissionType int32) func(ctx *gin.Context) {
	return func(ctx *gin.Context) {
		defer func() {
			if err := recover(); err != nil {
				log.Errorf("SensitiveCheck panic: %v", err)
			}
		}()
		//1.获取value值
		value := GetFieldValue(ctx, fieldName)
		if len(value) == 0 {
			return
		}
		//2.校验用户授权权限
		err := knowledgeGrantUser(ctx, value, permissionType)
		//3.返回结果
		if err != nil {
			gin_util.ResponseErrWithStatus(ctx, http.StatusBadRequest, err)
			ctx.Abort()
			return
		}
	}
}

// AuthKnowledge 校验知识库权限
func AuthKnowledge(fieldName string, permissionType int32) func(ctx *gin.Context) {
	return func(ctx *gin.Context) {
		defer func() {
			if err := recover(); err != nil {
				log.Errorf("SensitiveCheck panic: %v", err)
			}
		}()
		//1.获取value值
		value := GetFieldValue(ctx, fieldName)
		if len(value) == 0 {
			gin_util.ResponseErrWithStatus(ctx, http.StatusBadRequest, errors.New("knowledgeId is required"))
			ctx.Abort()
			return
		}
		//2.校验用户授权权限
		err := knowledgeGrantUser(ctx, value, permissionType)
		//3.返回结果
		if err != nil {
			gin_util.ResponseErrWithStatus(ctx, http.StatusBadRequest, err)
			ctx.Abort()
			return
		}
	}
}

func GetFieldValue(ctx *gin.Context, fieldName string) string {
	value := ctx.Query(fieldName)
	if len(value) > 0 {
		return value
	}
	if binding.MIMEJSON != ctx.ContentType() {
		return ""
	}
	//获取原始数据
	body, err := getRequestBody(ctx)
	if err != nil || len(body) == 0 {
		//获取对应filed的值
		log.Errorf("paramsMap error %s %v", fieldName, err)
		return ""
	}
	//还得写回body ，因为流只能读一次
	ctx.Request.Body = io.NopCloser(bytes.NewBuffer(body))

	//构造参数对应map
	paramsMap := make(map[string]interface{})
	err = json.Unmarshal(body, &paramsMap)
	if err != nil {
		return ""
	}
	//获取对应filed的值
	log.Infof("paramsMap %s", string(body))
	fieldValue := paramsMap[fieldName]
	if fieldValue == nil {
		return ""
	}
	retValue, ok := fieldValue.(string)
	if !ok {
		return ""
	}
	return retValue
}

func getRequestBody(c *gin.Context) ([]byte, error) {
	var body []byte
	if cb, ok := c.Get(gin.BodyBytesKey); ok {
		if cbb, ok := cb.([]byte); ok {
			body = cbb
		}
	}
	if body == nil {
		var err error
		body, err = io.ReadAll(c.Request.Body)
		if err != nil {
			return nil, err
		}
	}
	return body, nil
}

func searchKnowledgeId(ctx *gin.Context, docId string) (string, error) {
	docInfo, err := service.GetDocDetail(ctx, "", "", docId)
	if err != nil {
		return "", err
	}
	return docInfo.KnowledgeId, nil
}

func knowledgeGrantUser(ctx *gin.Context, knowledgeId string, permissionType int32) error {
	// userID
	userID, err := getContextUserId(ctx)
	if err != nil {
		return err
	}

	// orgID
	orgID := getOrgID(ctx)
	if len(orgID) == 0 {
		return errors.New("X-Org-Id is empty")
	}

	// check user knowledge permission
	if err = service.CheckKnowledgeUserPermission(ctx, userID, orgID, knowledgeId, permissionType); err != nil {
		return err
	}
	return nil
}

func getContextUserId(ctx *gin.Context) (string, error) {
	value, exists := ctx.Get(gin_util.USER_ID)
	if exists {
		return value.(string), nil
	}
	return getUserID(ctx)
}
