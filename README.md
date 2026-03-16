*Read this in other languages: [繁體中文](README_zh-TW.md).*

# Single-GPU Privacy Engine: Lightweight LLM-Empowered Differential Privacy Synthetic Data System
<!-- # Privacy-Enhancing LLM-Based Synthetic Dataset Generation -->

> 🏆 **Winner of the IEEE DSC 2025 Best Poster Award**
>
> The official implementation of our DSC 2025 paper: **[Privacy-Enhancing LLM-Based Synthetic Dataset Generation by LoRA Fine-Tuning and Prompting](https://doi.org/10.1109/DSC65356.2025.11260873)**.



## Project Overview

This project develops an end-to-end synthetic data generation system that integrates Large Language Models (LLMs) with Differential Privacy (DP), effectively mitigating privacy leakage and individual re-identification risks when sharing and analyzing highly sensitive data. By combining parameter-efficient LoRA fine-tuning with inference-time Laplace-perturbed sampling, we provide a regulation-compliant, secure data synthesis solution without incurring the massive computational overhead of traditional DP-SGD. Designed for both academic rigor and real-world industrial deployment, our framework offers the following core values:

* **The Challenge:** Industries such as healthcare, finance, and insurance possess incredibly valuable sensitive data. However, traditional privacy-preserving model training (e.g., DP-SGD) incurs prohibitive computational costs, severely hindering data analysis and cross-institutional collaboration under strict security standards.
* **Our Lightweight Solution:** We utilize the open-source [Llama-3.1-8B](https://huggingface.co/meta-llama/Meta-Llama-3.1-8B) model, combining parameter-efficient LoRA fine-tuning with an inference-time Batch Laplace noise mechanism. Users can flexibly adjust the privacy budget ($\epsilon$) to perfectly balance data utility and privacy security without altering the model's frozen backbone.
* **Extremely Low Hardware Barrier:** This technology drastically reduces the resources required for training and deployment. **A single consumer-level GPU (e.g., RTX 4090)** is sufficient to complete the end-to-end private data generation, significantly lowering the hardware costs and technical barriers for enterprises adopting secure AI.
* **Rigorous Privacy & Utility Auditing:** We integrate the EU-compliant [Anonymeter](https://github.com/statice/anonymeter) framework, proving our system effectively defends against singling-out, linkability, and inference attacks. Furthermore, downstream task testing using the [Sweetviz](https://github.com/fbdesignpro/sweetviz) visual analysis suite confirms that the synthetic data fully retains the statistical characteristics and high utility of the original dataset.


## Key Features

* **Parameter-Efficient Fine-Tuning**: Utilizes LoRA to adapt the open-source [Llama-3.1-8B](https://huggingface.co/meta-llama/Meta-Llama-3.1-8B) model. This allows the system to run on a single consumer-level GPU while keeping the backbone frozen.


* **Inference-Time Differential Privacy**: Enforces $(\epsilon, \delta)$-DP by directly injecting calibrated Laplace noise into the model's pre-softmax token-probability vector (logits) during prompt sampling.


* **Built-in Privacy Auditing**: Integrates [Anonymeter](https://github.com/statice/anonymeter) (aligned with EU Article 29 WP guidelines) to seamlessly evaluate Singling-out, Linkability, and Inference risks. Experiments on the UCI Adult dataset show an average risk drop of ~75%.



## System Workflow

Our pipeline consists of three main steps driven by a single configuration file:

1. **Domain Corpus Curation and LoRA Fine-Tuning**: Converting structured records into natural-language descriptions and fine-tuning the LLM with trainable low-rank matrices.


2. **Laplace-Perturbed Prompt Sampling**: Executing a two-stage prompt (template + self-refinement) to generate both a *Raw-Generated* pass and a *DP-Semantic* pass using calibrated Laplace noise.


3. **Privacy Audit**: Quantifying the privacy leakage of both paired corpora to ensure safety and utility.


## Results (UCI Adult Dataset)

Comparing the Raw-Generated texts with our DP-Synthetic datasets:

| Metric | Raw-Generated (AUC/ACC) | DP-Semantic (AUC/ACC) |
| --- | --- | --- |
| **Singling-Out** (multivariate) | $0.99 \pm 0.0030$ | $0.12 \pm 0.0216$ |
| **Linkability** ($k=10$) | $0.99 \pm 0.0003$ | $0.17 \pm 0.0100$ |

*(Metrics demonstrate a ~75% reduction in re-identification risks with minimal loss of semantic fluency)*.

## Citation

If you find this repository useful in your research, please consider citing our paper:

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

## Acknowledgments

This work was supported by the Taiwan National Science and Technology Council (NSTC) under Grant Nos. 114-2221-E-027-109 and 113-2622-8-027-008-SB.
