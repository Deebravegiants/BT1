# [H] vllm: Malicious model to RCE by torch.load in hf_model_weights_iterator

## Summary
Severity: High
Advisory: GHSA-rh4j-5rhw-hr54
CVE: CVE-2025-24357
CWE: CWE-502
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-01-27
Source: https://github.com/advisories/GHSA-rh4j-5rhw-hr54
Type: github-advisory

## Affected
- PyPI: `vllm` — affected >=0 <0.7.0

## Details
### Description
The vllm/model_executor/weight_utils.py implements hf_model_weights_iterator to load the model checkpoint, which is downloaded from huggingface. It use torch.load function and weights_only parameter is default value False. There is a security warning on https://pytorch.org/docs/stable/generated/torch.load.html, when torch.load load a malicious pickle data it will execute arbitrary code during unpickling.

### Impact
This vulnerability can be exploited to execute arbitrary codes and OS commands in the victim machine who fetch the pretrained repo remotely.

Note that most models now use the safetensors format, which is not vulnerable to this issue.

### References
* https://pytorch.org/docs/stable/generated/torch.load.html
* Fix: https://github.com/vllm-project/vllm/pull/12366

## References
- https://github.com/vllm-project/vllm/security/advisories/GHSA-rh4j-5rhw-hr54
- https://nvd.nist.gov/vuln/detail/CVE-2025-24357
- https://github.com/vllm-project/vllm/pull/12366
- https://github.com/vllm-project/vllm/commit/d3d6bb13fb62da3234addf6574922a4ec0513d04
- https://github.com/pypa/advisory-database/tree/main/vulns/vllm/PYSEC-2025-58.yaml
- https://github.com/vllm-project/vllm
- https://github.com/vllm-project/vllm/releases/tag/v0.7.0
- https://pytorch.org/docs/stable/generated/torch.load.html
