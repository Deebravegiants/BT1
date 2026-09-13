# [H] NVIDIA NeMo Framework Deserializes Untrusted Data

## Summary
Severity: High
Advisory: GHSA-hvjw-vp7g-39h5
CVE: CVE-2025-33253
CWE: CWE-502
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-02-18
Source: https://github.com/advisories/GHSA-hvjw-vp7g-39h5
Type: github-advisory

## Affected
- PyPI: `nemo-toolkit` — affected >=0 <2.6.1

## Details
NVIDIA NeMo Framework contains a vulnerability where an attacker could cause remote code execution by convincing a user to load a maliciously crafted file. A successful exploit of this vulnerability might lead to code execution, denial of service, information disclosure, and data tampering.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-33253
- https://github.com/NVIDIA-NeMo/NeMo
- https://nvidia.custhelp.com/app/answers/detail/a_id/5762
- https://www.cve.org/CVERecord?id=CVE-2025-33253
