# [M] Conda-build Vulnerable to Path Traversal via Malicious Tar File

## Summary
Severity: Medium
Advisory: CVE-2025-32799
Aliases: GHSA-h499-pxgj-qh5h
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:P/VC:L/VI:H/VA:L/SC:N/SI:N/SA:N/E:P)
Published: 2025-06-16
Source: https://osv.dev/vulnerability/CVE-2025-32799
Type: osv

## Details
Conda-build contains commands and tools to build conda packages. Prior to version 25.4.0, the conda-build processing logic is vulnerable to path traversal (Tarslip) attacks due to improper sanitization of tar entry paths. Attackers can craft tar archives containing entries with directory traversal sequences to write files outside the intended extraction directory. This could lead to arbitrary file overwrites, privilege escalation, or code execution if sensitive locations are targeted. This issue has been patched in version 25.4.0.

## References
- https://github.com/conda/conda-build/blob/834448b995eee02cf1c2e7ca97bcfa9affc77ee5/conda_build/convert.py
- https://github.com/conda/conda-build/blob/834448b995eee02cf1c2e7ca97bcfa9affc77ee5/conda_build/render.py
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/32xxx/CVE-2025-32799.json
- https://github.com/conda/conda-build/security/advisories/GHSA-h499-pxgj-qh5h
- https://nvd.nist.gov/vuln/detail/CVE-2025-32799
- https://github.com/conda/conda-build/commit/bdf5e0022cec9a0c1378cca3f2dc8c92b4834673
