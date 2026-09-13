# [H] CVE-2022-28184

## Summary
Severity: High
Advisory: CVE-2022-28184
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-05-17
Source: https://osv.dev/vulnerability/CVE-2022-28184
Type: osv

## Details
NVIDIA GPU Display Driver for Windows and Linux contains a vulnerability in the kernel mode layer (nvlddmkm.sys) handler for DxgkDdiEscape, where an unprivileged regular user can access administrator- privileged registers, which may lead to denial of service, information disclosure, and data tampering.

## References
- https://security.gentoo.org/glsa/202310-02
- https://nvidia.custhelp.com/app/answers/detail/a_id/5353
