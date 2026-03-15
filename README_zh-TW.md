
# 基於大型語言模型與隱私強化的合成資料集生成

> 本專案為 DSC 2025 論文的官方程式碼實作：**[Privacy-Enhancing LLM-Based Synthetic Dataset Generation by LoRA Fine-Tuning and Prompting](https://doi.org/10.1109/DSC65356.2025.11260873)**。

本開源庫提供了一個端到端 (end-to-end) 且可重現的工作流程，旨在使用大型語言模型 (LLM) 生成具備隱私保護的合成資料集。透過結合參數高效的 LoRA 微調 (parameter-efficient LoRA fine-tuning) 與推論期的拉普拉斯擾動採樣 (inference-time Laplace-perturbed sampling)，我們提供了一個符合法規的安全資料合成方案，且無需承擔 DP-SGD 龐大的計算開銷。

## 主要特色

* **參數高效微調 (Parameter-Efficient Fine-Tuning)**：使用 LoRA 技術來微調開源的 `Llama-3.1-8B` 模型。這使得系統可以在凍結骨幹網路的情況下，僅使用單張消費級 GPU 即可運行。
* **推論期差分隱私 (Inference-Time Differential Privacy)**：透過在提示詞採樣 (prompt sampling) 期間，將經過校準的拉普拉斯雜訊直接注入模型 softmax 前的 token 機率向量 (logits) 中，來強制滿足 $(\epsilon, \delta)$-DP。
* **內建隱私稽核 (Built-in Privacy Auditing)**：整合了 [Anonymeter](https://github.com/statice/anonymeter)（符合歐盟第 29 條工作小組指南），評估單一化風險 (Singling-out)、可連結性風險 (Linkability) 及推論風險 (Inference risks)。在 UCI Adult 資料集上的實驗顯示，平均風險降低了約 75%。

## 系統工作流程

我們的 pipeline 包含三個主要步驟，皆可透過單一設定檔來統一控制：

1. **領域語料庫策劃與 LoRA 微調**：將結構化紀錄轉換為自然語言描述，並使用可訓練的 low-rank matrices 來微調 LLM。
2. **拉普拉斯擾動提示採樣**：執行兩階段提示（模板 + 自我完善），透過校準的拉普拉斯雜訊進行推論，分別生成「原始生成 (Raw-Generated)」與「DP 語意 (DP-Semantic)」兩種版本的資料集。
3. **隱私稽核**：量化這兩組配對語料庫的隱私洩漏情況，以確保安全性與實用性。


## 實驗結果 (UCI Adult 資料集)

比較「原始生成文本」與我們的「DP 合成資料集」：

| 指標 (Metric) | 原始生成 (Raw-Generated) (AUC/ACC) | DP 語意 (DP-Semantic) (AUC/ACC) |
| --- | --- | --- |
| **單一化風險 (Singling-Out)** (多變數) | $0.99 \pm 0.0030$ | $0.12 \pm 0.0216$ |
| **可連結性風險 (Linkability)** ($k=10$) | $0.99 \pm 0.0003$ | $0.17 \pm 0.0100$ |

*(各項指標顯示，重新識別風險降低了約 75%，且語意流暢度的損失極小)。*

## 📝 引用 (Citation)

如果您認為本專案對您的研究有幫助，請考慮引用我們的論文：
*(等 DOI 或是 arXiv 連結出來後，可以把實際的 BibTeX 貼在這裡)*

```bibtex
@INPROCEEDINGS{11260873,
  author={Hung, Sheng-Chieh and Chang, Chen-Fan and Chen, Yu-Chi and Chang, Yu-Ming and Lin, Yu-Ta and Lin, Michael and Lee, Wei-Bin},
  booktitle={2025 IEEE Conference on Dependable and Secure Computing (DSC)}, 
  title={Privacy-Enhancing LLM-Based Synthetic Dataset Generation by LoRA Fine-Tuning and Prompting}, 
  year={2025},
  volume={},
  number={},
  pages={1-2},
  keywords={Measurement;Data privacy;Large language models;Noise;Pipelines;Graphics processing units;Protection;Synthetic data;Guidelines;Large Language Models;Dataset Generation;Fine-tuning;Data Privacy;Privacy Analysis},
  doi={10.1109/DSC65356.2025.11260873}}
```

## 致謝 (Acknowledgments)

本研究由國家科學及技術委員會 (NSTC) 補助支持（計畫編號：114-2221-E-027-109 及 113-2622-8-027-008-SB）。
