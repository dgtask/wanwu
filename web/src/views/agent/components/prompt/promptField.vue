
<template>
  <div class="compare-container">
    <div class="compare-top">
      <div class="block prompt-box drawer-info">
        <div class="promptTitle">
          <h3>{{ $t('agent.form.systemPrompt') }}</h3>
          <div class="prompt-title-icon">
            <el-tooltip
              class="item"
              effect="dark"
              :content="$t('agent.form.submitToPrompt')"
              placement="top-start"
            >
              <span class="el-icon-folder-add tool-icon" @click="handleShowPrompt"></span>
            </el-tooltip>
            <el-tooltip
              class="item"
              effect="dark"
              :content="$t('tempSquare.promptOptimize')"
              placement="top-start"
            >
              <span class="el-icon-s-help tool-icon" @click="showPromptOptimize"></span>
            </el-tooltip>
            <el-tooltip
              class="item"
              effect="dark"
              :content="$t('tempSquare.promptCompare')"
              placement="top-start"
            >
              <span class="tool-icon" @click="showPromptCompare">
                <img :src="require('@/assets/imgs/temp-compare.png')" />
              </span>
            </el-tooltip>
          </div>
        </div>
        <div class="rl prompt-input">
          <el-input
            class="desc-input"
            v-model="systemPrompt"
            :placeholder="$t('agent.form.promptTips')"
            type="textarea"
            show-word-limit
            :rows="4"
          ></el-input>
        </div>
      </div>
    </div>
    <div class="compare-bottom">
      <div class="compare-bottom-title">调试预览</div>
      <div class="compare-bottom-content">
        <div v-show="echo" class="session rl echo">
            <Prologue  :editForm="editForm" @setProloguePrompt="setProloguePrompt" :isBigModel="true" />
        </div>
        <!--对话-->
        <div v-show="!echo" class="center-session">
            <SessionComponentSe
                    ref="session-com"
                    class="component"
                    :sessionStatus="sessionStatus"
                    @clearHistory="clearHistory"
                    @refresh="refresh"
                    :type="type"
                    @queryCopy="queryCopy"
                    :defaultUrl="editForm.avatar.path"
            />
            </div>
        </div>
    </div>
  </div>
</template>

<script>
import Prologue from '../Prologue.vue'
import SessionComponentSe from '../SessionComponentSe.vue'

export default {
  name: 'PromptCompare',
  components: {
    Prologue,
    SessionComponentSe
  },
  data() {
    return {
      systemPrompt: '',
      echo: true,
      editForm: {
        avatar: { path: '' }
      },
      sessionStatus: 0,
      type: 'agent'
    }
  },
  methods: {
    handleShowPrompt() {},
    showPromptOptimize() {},
    showPromptCompare() {},
    setProloguePrompt() {},
    clearHistory() {},
    refresh() {},
    queryCopy() {}
  }
}
</script>

<style scoped lang="scss">
.compare-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: 16px;
  box-sizing: border-box;
}

.compare-top {
  flex: 2;
  min-height: 20%;
}

.compare-bottom {
  flex: 8;
  margin-top: 20px;
  border-radius: 8px;
}

.compare-bottom-title {
  font-size: 16px;
  font-weight: 600;
  padding: 12px 20px;
}

.compare-bottom-content {
  height: calc(100% - 49px);
  overflow: auto;
  padding: 16px;
  box-sizing: border-box;
}

.compare-bottom-content .session,
.compare-bottom-content .center-session {
  height: 100%;
}

.block {
  border-radius: 8px;
  padding: 10px 20px;
}

.drawer-info {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.promptTitle {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0 0;
  h3 {
    font-size: 16px;
    font-weight: 800;
  }
}

.prompt-title-icon {
  display: flex;
  align-items: center;
  span {
    font-size: 16px;
    color: #5c6ac4;
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    margin-left: 10px;
  }
  .tool-icon {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    background: #e0e7ff;
    color: $color;
    img {
      width: 16px;
      height: 16px;
    }
  }
}

.prompt-input {
  padding: 10px 0;
  flex: 1;
  display: flex;
  flex-direction: column;
}

.desc-input /deep/ .el-textarea__inner {
  background-color: transparent !important;
  border: 1px solid #d3d7dd !important;
  padding: 15px;
}
</style>

