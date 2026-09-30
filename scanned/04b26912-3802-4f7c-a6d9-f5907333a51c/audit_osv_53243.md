# [H] CVE-2022-34670

## Summary
Severity: High
Advisory: CVE-2022-34670
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-12-30
Source: https://osv.dev/vulnerability/CVE-2022-34670
Type: osv

## Details
NVIDIA GPU Display Driver for Linux contains a vulnerability in the kernel mode layer handler, where an unprivileged regular user can cause truncation errors when casting a primitive to a primitive of smaller size causes data to be lost in the conversion, which may lead to denial of service or information disclosure.

## References
- https://nvidia.custhelp.com/app/answers/detail/a_id/5415
- https://security.gentoo.org/glsa/202310-02
- https://lists.debian.org/debian-lts-announce/2023/05/msg00010.html
