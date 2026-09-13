# [C] CVE-2025-54952

## Summary
Severity: Critical
Advisory: CVE-2025-54952
Aliases: GHSA-33r8-vrx9-rmcv, PYSEC-2026-1351
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-08-07
Source: https://osv.dev/vulnerability/CVE-2025-54952
Type: osv

## Details
An integer overflow vulnerability in the loading of ExecuTorch models can cause smaller-than-expected memory regions to be allocated, potentially resulting in code execution or other undesirable effects. This issue affects ExecuTorch prior to commit 8f062d3f661e20bb19b24b767b9a9a46e8359f2b.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/54xxx/CVE-2025-54952.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-54952
- https://www.facebook.com/security/advisories/cve-2025-54952
- https://github.com/pytorch/executorch/commit/8f062d3f661e20bb19b24b767b9a9a46e8359f2b
