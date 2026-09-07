# [C] PyTorch: `torch.load` with `weights_only=True` leads to remote code execution

## Summary
Severity: Critical
Advisory: GHSA-53q9-r3pm-6pq6
CVE: CVE-2025-32434
CWE: CWE-502
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-04-18
Source: https://github.com/advisories/GHSA-53q9-r3pm-6pq6
Type: github-advisory

## Affected
- PyPI: `torch` — affected >=0 <2.6.0

## Details
# Description
I found a Remote Command Execution (RCE) vulnerability in PyTorch. When loading model using torch.load with weights_only=True, it can still achieve RCE.  

# Background knowledge
https://github.com/pytorch/pytorch/security 
 As you can see, the PyTorch official documentation considers using `torch.load()` with `weights_only=True` to be safe.
![image](https://github.com/user-attachments/assets/fdaa8520-d66a-473a-ab1f-163d793de298)
Since everyone knows that weights_only=False is unsafe, so they will use the  weights_only=True to mitigate the seucirty issue.
But now, I just proved that even if you use weights_only=True, it can still achieve RCE.

# Credit
This vulnerability was found by Ji'an Zhou.

## References
- https://github.com/pytorch/pytorch/security/advisories/GHSA-53q9-r3pm-6pq6
- https://nvd.nist.gov/vuln/detail/CVE-2025-32434
- https://github.com/pytorch/pytorch/commit/8d4b8a920a2172523deb95bf20e8e52d50649c04
- https://github.com/pypa/advisory-database/tree/main/vulns/torch/PYSEC-2025-41.yaml
- https://github.com/pytorch/pytorch
