# [M] CVE-2022-34680

## Summary
Severity: Medium
Advisory: CVE-2022-34680
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-12-30
Source: https://osv.dev/vulnerability/CVE-2022-34680
Type: osv

## Details
NVIDIA GPU Display Driver for Linux contains a vulnerability in the kernel mode layer handler, where an integer truncation can lead to an out-of-bounds read, which may lead to denial of service.

## References
- https://nvidia.custhelp.com/app/answers/detail/a_id/5415
- https://security.gentoo.org/glsa/202310-02
- https://lists.debian.org/debian-lts-announce/2023/05/msg00010.html
