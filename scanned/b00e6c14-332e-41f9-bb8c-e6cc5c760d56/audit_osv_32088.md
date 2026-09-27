# [H] CVE-2025-23306

## Summary
Severity: High
Advisory: CVE-2025-23306
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-08-13
Source: https://osv.dev/vulnerability/CVE-2025-23306
Type: osv

## Details
NVIDIA Megatron-LM for all platforms contains a vulnerability in the megatron/training/
arguments.py component where an attacker could cause a code injection issue by providing a malicious input. A successful exploit of this vulnerability may lead to code execution, escalation of privileges, information disclosure, and data tampering.

## References
- https://nvidia.custhelp.com/app/answers/detail/a_id/5685
- https://www.cve.org/CVERecord?id=CVE-2025-23306
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/23xxx/CVE-2025-23306.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-23306
