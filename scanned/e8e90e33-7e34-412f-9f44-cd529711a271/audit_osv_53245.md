# [M] CVE-2022-34674

## Summary
Severity: Medium
Advisory: CVE-2022-34674
CVSS: 6.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N)
Published: 2022-12-30
Source: https://osv.dev/vulnerability/CVE-2022-34674
Type: osv

## Details
NVIDIA GPU Display Driver for Linux contains a vulnerability in the kernel mode layer handler, where a helper function maps more physical pages than were requested, which may lead to undefined behavior or an information leak.

## References
- https://nvidia.custhelp.com/app/answers/detail/a_id/5415
- https://security.gentoo.org/glsa/202310-02
- https://lists.debian.org/debian-lts-announce/2023/05/msg00010.html
