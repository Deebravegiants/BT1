# [M] CVE-2023-0188

## Summary
Severity: Medium
Advisory: CVE-2023-0188
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-04-01
Source: https://osv.dev/vulnerability/CVE-2023-0188
Type: osv

## Details
NVIDIA GPU Display Driver for Windows and Linux contains a vulnerability in the kernel mode layer handler, where an unprivileged user can cause improper restriction of operations within the bounds of a memory buffer cause an out-of-bounds read, which may lead to denial of service.

## References
- https://nvidia.custhelp.com/app/answers/detail/a_id/5452
- https://security.gentoo.org/glsa/202310-02
