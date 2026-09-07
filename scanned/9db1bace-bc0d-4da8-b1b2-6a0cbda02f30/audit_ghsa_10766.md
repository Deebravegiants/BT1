# [C] NVIDIA NVFlare Dashboard: Authorization bypass through user-controlled key via user management and authentication system

## Summary
Severity: Critical
Advisory: GHSA-jqp3-qrgh-4846
CVE: CVE-2026-24178
CWE: CWE-639
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-28
Source: https://github.com/advisories/GHSA-jqp3-qrgh-4846
Type: github-advisory

## Affected
- PyPI: `nvflare` — affected >=0 <2.7.2

## Details
NVIDIA NVFlare Dashboard contains a vulnerability in the user management and authentication system where an unauthenticated attacker may cause authorization bypass through user-controlled key. A successful exploit of this vulnerability may lead to privilege escalation, data tampering, information disclosure, code execution, and denial of service.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-24178
- https://github.com/NVIDIA/NVFlare
- https://github.com/pypa/advisory-database/tree/main/vulns/nvflare/PYSEC-2026-100.yaml
- https://nvidia.custhelp.com/app/answers/detail/a_id/5819
- https://www.cve.org/CVERecord?id=CVE-2026-24178
