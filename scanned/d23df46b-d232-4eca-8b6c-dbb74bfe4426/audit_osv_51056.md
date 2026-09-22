# [M] CVE-2021-1053

## Summary
Severity: Medium
Advisory: CVE-2021-1053
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-01-08
Source: https://osv.dev/vulnerability/CVE-2021-1053
Type: osv

## Details
NVIDIA GPU Display Driver for Windows and Linux, all versions, contains a vulnerability in the kernel mode layer (nvlddmkm.sys) handler for DxgkDdiEscape or IOCTL in which improper validation of a user pointer may lead to denial of service.

## References
- https://nvidia.custhelp.com/app/answers/detail/a_id/5142
- https://security.gentoo.org/glsa/202310-02
