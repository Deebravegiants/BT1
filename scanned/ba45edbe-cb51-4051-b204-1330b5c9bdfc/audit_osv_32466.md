# [C] CVE-2025-30404

## Summary
Severity: Critical
Advisory: CVE-2025-30404
Aliases: GHSA-hj95-mhgf-jxc4, PYSEC-2026-335
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-08-07
Source: https://osv.dev/vulnerability/CVE-2025-30404
Type: osv

## Details
An integer overflow vulnerability in the loading of ExecuTorch models can cause overlapping allocations, potentially resulting in code execution or other undesirable effects. This issue affects ExecuTorch prior to commit d158236b1dc84539c1b16843bc74054c9dcba006.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/30xxx/CVE-2025-30404.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-30404
- https://www.facebook.com/security/advisories/cve-2025-30404
- https://github.com/pytorch/executorch/commit/d158236b1dc84539c1b16843bc74054c9dcba006
