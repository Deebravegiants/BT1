# [M] CVE-2019-15902

## Summary
Severity: Medium
Advisory: CVE-2019-15902
CVSS: 5.6 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:C/C:H/I:N/A:N)
Published: 2019-09-04
Source: https://osv.dev/vulnerability/CVE-2019-15902
Type: osv

## Details
A backporting error was discovered in the Linux stable/longterm kernel 4.4.x through 4.4.190, 4.9.x through 4.9.190, 4.14.x through 4.14.141, 4.19.x through 4.19.69, and 5.2.x through 5.2.11. Misuse of the upstream "x86/ptrace: Fix possible spectre-v1 in ptrace_get_debugreg()" commit reintroduced the Spectre vulnerability that it aimed to eliminate. This occurred because the backport process depends on cherry picking specific commits, and because two (correctly ordered) code lines were swapped.

## References
- https://usn.ubuntu.com/4163-2/
- https://usn.ubuntu.com/4157-1/
- https://usn.ubuntu.com/4157-2/
- https://usn.ubuntu.com/4162-1/
- https://usn.ubuntu.com/4162-2/
- https://usn.ubuntu.com/4163-1/
- https://www.debian.org/security/2019/dsa-4531
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00064.html
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00066.html
- https://lists.debian.org/debian-lts-announce/2019/10/msg00000.html
- https://seclists.org/bugtraq/2019/Sep/41
- https://security.netapp.com/advisory/ntap-20191004-0001/
- https://grsecurity.net/teardown_of_a_failed_linux_lts_spectre_fix.php
