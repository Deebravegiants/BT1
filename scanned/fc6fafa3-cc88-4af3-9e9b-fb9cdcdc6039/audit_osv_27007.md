# [H] CVE-2024-0129

## Summary
Severity: High
Advisory: CVE-2024-0129
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-10-15
Source: https://osv.dev/vulnerability/CVE-2024-0129
Type: osv

## Details
NVIDIA NeMo contains a vulnerability in SaveRestoreConnector where a user may cause a path traversal issue via an unsafe .tar file extraction. A successful exploit of this vulnerability may lead to code execution and data tampering.

## References
- https://nvidia.custhelp.com/app/answers/detail/a_id/5580
