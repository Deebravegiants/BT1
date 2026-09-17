# [H] CVE-2021-1056

## Summary
Severity: High
Advisory: CVE-2021-1056
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2021-01-08
Source: https://osv.dev/vulnerability/CVE-2021-1056
Type: osv

## Details
NVIDIA GPU Display Driver for Linux, all versions, contains a vulnerability in the kernel mode layer (nvidia.ko) in which it does not completely honor operating system file system permissions to provide GPU device-level isolation, which may lead to denial of service or information disclosure.

## References
- https://lists.debian.org/debian-lts-announce/2022/01/msg00013.html
- https://nvidia.custhelp.com/app/answers/detail/a_id/5142
- https://security.gentoo.org/glsa/202310-02
