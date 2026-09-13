# [M] CVE-2022-1462

## Summary
Severity: Medium
Advisory: CVE-2022-1462
CVSS: 6.3 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2022-06-02
Source: https://osv.dev/vulnerability/CVE-2022-1462
Type: osv

## Details
An out-of-bounds read flaw was found in the Linux kernel’s TeleTYpe subsystem. The issue occurs in how a user triggers a race condition using ioctls TIOCSPTLCK and TIOCGPTPEER and TIOCSTI and TCXONC with leakage of memory in the flush_to_ldisc function. This flaw allows a local user to crash the system or read unauthorized random data from memory.

## References
- https://lists.debian.org/debian-lts-announce/2022/10/msg00000.html
- https://bugzilla.redhat.com/show_bug.cgi?id=2078466
- https://seclists.org/oss-sec/2022/q2/155
