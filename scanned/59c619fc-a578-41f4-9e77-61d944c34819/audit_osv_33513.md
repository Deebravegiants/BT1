# [C] CVE-2025-45146

## Summary
Severity: Critical
Advisory: CVE-2025-45146
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-08-11
Source: https://osv.dev/vulnerability/CVE-2025-45146
Type: osv

## Details
ModelCache for LLM through v0.2.0 was discovered to contain an deserialization vulnerability via the component /manager/data_manager.py. This vulnerability allows attackers to execute arbitrary code via supplying crafted data.

## References
- https://github.com/EDMPL/Vulnerability-Research/blob/main/CVE-2025-45146/README.md
- https://github.com/codefuse-ai/ModelCache/blob/e053e0d57b532d4ad9378d2f31bb85a009b77d64/modelcache/manager/data_manager.py#L84C1-L84C43
- https://github.com/codefuse-ai/ModelCache/blob/e053e0d57b532d4ad9378d2f31bb85a009b77d64/modelcache/manager/factory.py#L18C1-L18C71
- https://pytorch.org/docs/stable/generated/torch.load.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/45xxx/CVE-2025-45146.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-45146
