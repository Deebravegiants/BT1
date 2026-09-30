# [H] CVE-2022-34677

## Summary
Severity: High
Advisory: CVE-2022-34677
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H)
Published: 2022-12-30
Source: https://osv.dev/vulnerability/CVE-2022-34677
Type: osv

## Details
NVIDIA GPU Display Driver for Linux contains a vulnerability in the kernel mode layer handler, where an unprivileged regular user can cause an integer to be truncated, which may lead to denial of service or data tampering.

## References
- https://nvidia.custhelp.com/app/answers/detail/a_id/5415
- https://security.gentoo.org/glsa/202310-02
- https://lists.debian.org/debian-lts-announce/2023/05/msg00010.html
