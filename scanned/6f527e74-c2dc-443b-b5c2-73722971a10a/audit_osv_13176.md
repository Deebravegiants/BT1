# [M] CVE-2018-18398

## Summary
Severity: Medium
Advisory: CVE-2018-18398
CVSS: 4.7 (CVSS:3.0/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-10-19
Source: https://osv.dev/vulnerability/CVE-2018-18398
Type: osv

## Details
Xfce Thunar 1.6.15, when Xfce 4.12 is used, mishandles the IBus-Unikey input method for file searches within File Manager, leading to an out-of-bounds read and SEGV. This could potentially be exploited by an arbitrary local user who creates files in /tmp before the victim uses this input method.

## References
- https://0xd0ff9.wordpress.com/2018/10/18/cve-2018-18398/
