<template>
  <div class="compare-container">
    <div class="compare-header">
      <div class="compare-header-left">
        <span class="el-icon-arrow-left go-back" @click="goBack"></span>
        <h3>提示词对比</h3>
      </div>
      <el-button type="primary" size="small" @click="addPromptField">
        <i class="el-icon-plus" style="margin-right:4px;"></i>
        增加提示词
      </el-button>
    </div>
    <div class="compare-content">
      <div class="compare-middle">
        <div class="prompt-field-list">
          <div
            class="prompt-field-item"
            v-for="field in promptFields"
            :key="field.id"
          >
            <PromptField />
          </div>
        </div>
      </div>
      <div class="compare-bottom">
        <EditableDivV3
          ref="editable"
          source="promptCompare"
          :fileTypeArr="fileTypeArr"
          :showModelSelect="false"
          :currentModel="currentModel"
          :isModelDisable="false"
          type="compare"
        />
      </div>
    </div>
  </div>
</template>

<script>
import PromptField from './promptField.vue'
import EditableDivV3 from '../EditableDivV3'

export default {
  name: 'PromptCompare',
  components: {
    PromptField,
    EditableDivV3
  },
  data() {
    return {
      promptFields: [{ id: Date.now() }],
      fileTypeArr: [],
      currentModel: null
    }
  },
  methods: {
    addPromptField() {
      this.promptFields.push({ id: Date.now() + Math.random() })
    },
    goBack(){

    }
  }
}
</script>

<style scoped lang="scss">
.compare-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  width: 100%;
  padding:0 10px;
  box-sizing: border-box;
}

.compare-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding:24px 0 14px 30px;
  border-bottom: 1px solid #eaeaea;
  .compare-header-left{
    display: flex;
    align-items: center;
    .go-back{
      font-size: 18px;
      cursor: pointer;
    }
    h3{
      font-size: 18px;
      font-weight: 800;
      color: #434c6c;
      margin-left: 10px;
  } 
  }
}
.compare-content{
  flex: 1;
  padding:10px 0;
  .compare-middle {
    height:88%;
    min-height: 0;
    margin-bottom: 16px;
    overflow: hidden;
  }

  .prompt-field-list {
    display: flex;
    gap: 16px;
    height: 100%;
    overflow-x: auto;
    padding-bottom: 8px;
  }

  .prompt-field-item {
    flex: 1;
    min-width: 360px;
    height: 100%;
  }

  .compare-bottom {
    height:calc(100% - 88% - 16px);
  }
}

</style>
