# [M] CVE-2023-3397

## Summary
Severity: Medium
Advisory: CVE-2023-3397
CVSS: 6.3 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2023-11-01
Source: https://osv.dev/vulnerability/CVE-2023-3397
Type: osv

## Details
A race condition occurred between the functions lmLogClose and txEnd in JFS, in the Linux Kernel, executed in different threads. This flaw allows a local attacker with normal user privileges to crash the system or leak internal kernel information.

## References
- https://access.redhat.com/security/cve/CVE-2023-3397
- https://www.spinics.net/lists/kernel/msg4788636.html
- https://www.spinics.net/lists/kernel/msg4788636.html
- https://bugzilla.redhat.com/show_bug.cgi?id=2217271
