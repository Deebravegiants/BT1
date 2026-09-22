# [H] CVE-2024-0110

## Summary
Severity: High
Advisory: CVE-2024-0110
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2024-08-31
Source: https://osv.dev/vulnerability/CVE-2024-0110
Type: osv

## Details
NVIDIA CUDA Toolkit contains a vulnerability in command `cuobjdump` where a user may cause an out-of-bound write by passing in a malformed ELF file. A successful exploit of this vulnerability may lead to code execution or denial of service.

## References
- https://nvidia.custhelp.com/app/answers/detail/a_id/5564
