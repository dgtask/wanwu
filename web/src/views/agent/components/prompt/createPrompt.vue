<template>
  <el-dialog
    :title="$t('agent.promptTemplate.submitToPromptLibrary')"
    :visible.sync="dialogVisible"
    width="40%"
    :close-on-click-modal="false"
    :before-close="handleClose"
    class="create-prompt-dialog"
  >
    <el-form 
      ref="form" 
      :model="form" 
      :rules="rules" 
      label-width="140px"
      label-position="left"
    >
      <el-form-item :label="$t('agent.promptTemplate.promptIcon') + ':'" prop="avatar" required>
        <el-upload
          class="avatar-uploader"
          action=""
          name="files"
          :show-file-list="false"
          :http-request="handleUploadImage"
          accept=".png,.jpg,.jpeg"
        >
          <div class="upload-icon-container">
            <img
              v-if="form.avatar && form.avatar.path"
              class="upload-icon-img"
              :src="basePath + '/user/api/' + form.avatar.path"
            />
            <div v-else class="upload-icon-placeholder">
              <i class="el-icon-plus"></i>
            </div>
          </div>
        </el-upload>
      </el-form-item>
      
      <el-form-item :label="$t('agent.promptTemplate.promptTitle') + ':'" prop="name" required class="form-item-vertical">
        <el-input
          v-model="form.name"
          :placeholder="$t('agent.promptTemplate.titleRequired')"
          maxlength="50"
          show-word-limit
        ></el-input>
      </el-form-item>
      
      <el-form-item :label="$t('agent.promptTemplate.promptDesc') + ':'" prop="desc" required class="form-item-vertical">
        <el-input
          type="textarea"
          v-model="form.desc"
          :placeholder="$t('agent.promptTemplate.descRequired')"
          :rows="3"
          maxlength="200"
          show-word-limit
        ></el-input>
      </el-form-item>
      
      <el-form-item :label="$t('agent.promptTemplate.promptContent') + ':'" prop="prompt" required class="form-item-vertical">
        <el-input
          type="textarea"
          v-model="form.prompt"
          :placeholder="$t('agent.promptTemplate.promptRequired')"
          :rows="6"
        ></el-input>
      </el-form-item>
    </el-form>
    
    <span slot="footer" class="dialog-footer">
      <el-button @click="handleClose">{{ $t('common.button.cancel') }}</el-button>
      <el-button type="primary" @click="handleSubmit">{{ $t('common.button.confirm') }}</el-button>
    </span>
  </el-dialog>
</template>

<script>
import { uploadAvatar } from "@/api/user";
import {createPromptTemplate } from "@/api/promptTemplate";

export default {
  name: 'CreatePrompt',
  props: {
    promptText: {
      type: String,
      default: ''
    }
  },
  data() {
    return {
      basePath: this.$basePath,
      dialogVisible: false,
      form: {
        name: '',
        desc: '',
        avatar: {
          key: '',
          path: ''
        },
        prompt: ''
      },
      rules: {
        name: [
          { required: true, message: this.$t('agent.promptTemplate.titleRequired'), trigger: 'blur' },
          { max: 50, message: this.$t('agent.promptTemplate.titleMaxLength'), trigger: 'blur' }
        ],
        desc: [
          { required: true, message: this.$t('agent.promptTemplate.descRequired'), trigger: 'blur' },
          { max: 200, message: this.$t('agent.promptTemplate.descMaxLength'), trigger: 'blur' }
        ],
        prompt: [
          { required: true, message: this.$t('agent.promptTemplate.promptRequired'), trigger: 'blur' }
        ],
        avatar: [
          { required: true, message: this.$t('agent.promptTemplate.avatarRequired'), trigger: 'change' }
        ]
      }
    };
  },
  watch: {
    promptText(newVal) {
      if (newVal) {
        this.form.prompt = newVal;
      }
    }
  },
  methods: {
    handleUploadImage(data) {
      if (data.file) {
        this.uploadAvatar(data.file, 'avatar').then(res => {
          if (res.code === 0) {
            const { key, path } = res.data || {};
            this.form.avatar = { key, path };
            this.$refs.form.validateField('avatar');
          }
        })
      }
    },
    uploadAvatar(file, key) {
      const formData = new FormData();
      const config = { headers: { "Content-Type": "multipart/form-data" } };
      formData.append(key, file);
      return uploadAvatar(formData, config);
    },
    handleSubmit() {
      this.$refs.form.validate(async (valid) => {
        if (valid) {
          try {
            const res = await createPromptTemplate(this.form);
            if (res.code === 0) {
              this.$message.success(this.$t('agent.promptTemplate.submitSuccess'));
              this.handleClose();
              this.$emit('updateDetail');
            }
          } catch (error) {
            this.$message.error(this.$t('agent.promptTemplate.submitFail'));
          }
        }
      });
    },
    handleClose() {
      this.dialogVisible = false;
      this.$refs.form.resetFields();
      this.form = {
        name: '',
        desc: '',
        avatar: {
          key: '',
          path: ''
        },
        prompt: ''
      };
    },
    showDialog() {
      this.dialogVisible = true;
      this.$nextTick(() => {
        this.$refs.form.clearValidate();
      });
    }
  }
};
</script>

<style lang="scss" scoped>
.create-prompt-dialog {
  /deep/ .el-dialog__body {
    padding: 20px;
  }
  
  /deep/ .el-form-item__label {
    &::before {
      content: '*';
      color: #F56C6C;
      margin-right: 4px;
    }
  }
  
  /deep/ .form-item-vertical {
    .el-form-item__label {
      float: none;
      text-align: left;
      padding: 0 0 8px 0;
      line-height: 1.5;
    }
    
    .el-form-item__content {
      margin-left: 0 !important;
    }
  }
  
  .avatar-uploader {
    .upload-icon-container {
      width: 120px;
      height: 120px;
      border: 1px solid #DCDFE6;
      border-radius: 6px;
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      transition: all 0.3s;
      background-color: #F5F7FA;
      
      &:hover {
        border-color: #409EFF;
      }
      
      .upload-icon-img {
        width: 100%;
        height: 100%;
        object-fit: cover;
        border-radius: 6px;
      }
      
      .upload-icon-placeholder {
        width: 100%;
        height: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #8C939D;
        font-size: 28px;
      }
    }
  }
  
  /deep/ .el-textarea {
    .el-textarea__inner {
      resize: vertical;
    }
  }
  
  .dialog-footer {
    /deep/ .el-button--danger {
      background-color: #F56C6C;
      border-color: #F56C6C;
      
      &:hover {
        background-color: #f78989;
        border-color: #f78989;
      }
    }
  }
}
</style>

