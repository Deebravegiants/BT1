# [M] CVE-2023-25513

## Summary
Severity: Medium
Advisory: CVE-2023-25513
CVSS: 6.6 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:L/I:H/A:L)
Published: 2023-04-22
Source: https://osv.dev/vulnerability/CVE-2023-25513
Type: osv

## Details
NVIDIA CUDA toolkit for Linux and Windows contains a vulnerability in cuobjdump, where an attacker may cause an out-of-bounds read by tricking a user into running cuobjdump on a malformed input file. A successful exploit of this vulnerability may lead to limited denial of service, code execution, and limited information disclosure.

## References
- https://nvidia.custhelp.com/app/answers/detail/a_id/5456
