# [H] CVE-2025-23348

## Summary
Severity: High
Advisory: CVE-2025-23348
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-24
Source: https://osv.dev/vulnerability/CVE-2025-23348
Type: osv

## Details
NVIDIA Megatron-LM for all platforms contains a vulnerability in the pretrain_gpt script, where malicious data created by an attacker may cause a code injection issue. A successful exploit of this vulnerability may lead to code execution, escalation of privileges, information disclosure, and data tampering.

## References
- https://nvidia.custhelp.com/app/answers/detail/a_id/5698
- https://www.cve.org/CVERecord?id=CVE-2025-23348
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/23xxx/CVE-2025-23348.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-23348
