# [M] CVE-2018-10938

## Summary
Severity: Medium
Advisory: CVE-2018-10938
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-08-27
Source: https://osv.dev/vulnerability/CVE-2018-10938
Type: osv

## Details
A flaw was found in the Linux kernel present since v4.0-rc1 and through v4.13-rc4. A crafted network packet sent remotely by an attacker may force the kernel to enter an infinite loop in the cipso_v4_optptr() function in net/ipv4/cipso_ipv4.c leading to a denial-of-service. A certain non-default configuration of LSM (Linux Security Module) and NetLabel should be set up on a system before an attacker could leverage this flaw.

## References
- http://seclists.org/oss-sec/2018/q3/179
- http://www.securitytracker.com/id/1041569
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=40413955ee265a5e42f710940ec78f5450d49149
- https://lists.debian.org/debian-lts-announce/2018/10/msg00003.html
- https://usn.ubuntu.com/3797-1/
- https://usn.ubuntu.com/3797-2/
- http://www.securityfocus.com/bid/105154
- https://www.debian.org/security/2018/dsa-4308
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-10938
