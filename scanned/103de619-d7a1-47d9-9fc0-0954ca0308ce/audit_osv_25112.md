# [H] CVE-2023-31036

## Summary
Severity: High
Advisory: CVE-2023-31036
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-01-12
Source: https://osv.dev/vulnerability/CVE-2023-31036
Type: osv

## Details
NVIDIA Triton Inference Server for Linux and Windows contains a vulnerability where, when it is launched with the non-default command line option --model-control explicit, an attacker may use the model load API to cause a relative path traversal. A successful exploit of this vulnerability may lead to code execution, denial of service, escalation of privileges, information disclosure, and data tampering.

## References
- https://nvidia.custhelp.com/app/answers/detail/a_id/5509
