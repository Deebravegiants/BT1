# [H] NVIDIA NeMo Framework contains an RCE vulnerability in checkpoint loading

## Summary
Severity: High
Advisory: GHSA-m4jw-wgmf-889x
CVE: CVE-2026-24157
CWE: CWE-502
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-24
Source: https://github.com/advisories/GHSA-m4jw-wgmf-889x
Type: github-advisory

## Affected
- PyPI: `nemo-toolkit` — affected >=0 <2.6.2

## Details
NVIDIA NeMo Framework contains a vulnerability in checkpoint loading where an attacker could cause remote code execution. A successful exploit of this vulnerability might lead to code execution, escalation of privileges, information disclosure and data tampering.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-24157
- https://github.com/NVIDIA-NeMo/NeMo
- https://nvidia.custhelp.com/app/answers/detail/a_id/5800
- https://www.cve.org/CVERecord?id=CVE-2026-24157
