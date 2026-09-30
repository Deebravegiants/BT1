# [M] CVE-2024-0102

## Summary
Severity: Medium
Advisory: CVE-2024-0102
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2024-08-08
Source: https://osv.dev/vulnerability/CVE-2024-0102
Type: osv

## Details
NVIDIA CUDA Toolkit for all platforms contains a vulnerability in nvdisasm, where an attacker can cause an out-of-bounds read issue by deceiving a user into reading a malformed ELF file. A successful exploit of this vulnerability might lead to denial of service.

## References
- https://nvidia.custhelp.com/app/answers/detail/a_id/5548
