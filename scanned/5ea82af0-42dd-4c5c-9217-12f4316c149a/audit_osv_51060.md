# [M] CVE-2021-1093

## Summary
Severity: Medium
Advisory: CVE-2021-1093
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-07-22
Source: https://osv.dev/vulnerability/CVE-2021-1093
Type: osv

## Details
NVIDIA GPU Display Driver for Windows and Linux contains a vulnerability in firmware where the driver contains an assert() or similar statement that can be triggered by an attacker, which leads to an application exit or other behavior that is more severe than necessary, and may lead to denial of service or system crash.

## References
- https://lists.debian.org/debian-lts-announce/2022/01/msg00013.html
- https://security.gentoo.org/glsa/202310-02
- https://nvidia.custhelp.com/app/answers/detail/a_id/5211
