# [C] CVE-2025-24357 Malicious model remote code execution fix bypass with PyTorch < 2.6.0

## Summary
Severity: Critical
Advisory: GHSA-ggpf-24jw-3fcw
CWE: CWE-1395
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-04-23
Source: https://github.com/advisories/GHSA-ggpf-24jw-3fcw
Type: github-advisory

## Affected
- PyPI: `vllm` — affected >=0 <0.8.0

## Details
## Description

https://github.com/vllm-project/vllm/security/advisories/GHSA-rh4j-5rhw-hr54 reported a vulnerability where loading a malicious model could result in code execution on the vllm host. The fix applied to specify `weights_only=True` to calls to `torch.load()` did not solve the problem prior to PyTorch 2.6.0.

PyTorch has issued a new CVE about this problem: https://github.com/advisories/GHSA-53q9-r3pm-6pq6

This means that versions of vLLM using PyTorch before 2.6.0 are vulnerable to this problem.
## Background Knowledge
When users install VLLM according to the official manual
![image](https://github.com/user-attachments/assets/d17e0bdb-26f2-46d6-adf6-0b17e5ddf5c7)

But the version of PyTorch is specified in the requirements. txt file
![image](https://github.com/user-attachments/assets/94aad622-ad6d-4741-b772-c342727c58c7)

So by default when the user install VLLM, it will install the PyTorch with version 2.5.1
![image](https://github.com/user-attachments/assets/04ff31b0-aad1-490a-963d-00fda91da47b)

In CVE-2025-24357, weights_only=True was used for patching, but we know this is not secure.
Because we found that using Weights_only=True in pyTorch before 2.5.1 was unsafe

Here, we use this interface to prove that it is not safe.
![image](https://github.com/user-attachments/assets/0d86efcd-2aad-42a2-8ac6-cc96b054c925)


## Fix
update PyTorch version to 2.6.0

## Credit
This vulnerability was found By Ji'an Zhou and Li'shuo Song

## References
- https://github.com/pytorch/pytorch/security/advisories/GHSA-53q9-r3pm-6pq6
- https://github.com/vllm-project/vllm/security/advisories/GHSA-ggpf-24jw-3fcw
- https://github.com/vllm-project/vllm/security/advisories/GHSA-rh4j-5rhw-hr54
- https://github.com/vllm-project/vllm
