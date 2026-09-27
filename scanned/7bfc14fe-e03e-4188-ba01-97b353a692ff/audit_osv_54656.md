# [M] CVE-2024-24860

## Summary
Severity: Medium
Advisory: CVE-2024-24860
CVSS: 5.3 (CVSS:3.1/AV:A/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-02-05
Source: https://osv.dev/vulnerability/CVE-2024-24860
Type: osv

## Details
A race condition was found in the Linux kernel's bluetooth device driver in {min,max}_key_size_set() function. This can result in a null pointer dereference issue, possibly leading to a kernel panic or denial of service issue.

## References
- https://lists.debian.org/debian-lts-announce/2024/06/msg00016.html
- https://bugzilla.openanolis.cn/show_bug.cgi?id=8151
