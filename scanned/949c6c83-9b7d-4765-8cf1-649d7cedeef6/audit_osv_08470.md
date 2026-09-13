# [H] CVE-2016-3672

## Summary
Severity: High
Advisory: CVE-2016-3672
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-04-27
Source: https://osv.dev/vulnerability/CVE-2016-3672
Type: osv

## Details
The arch_pick_mmap_layout function in arch/x86/mm/mmap.c in the Linux kernel through 4.5.2 does not properly randomize the legacy base address, which makes it easier for local users to defeat the intended restrictions on the ADDR_NO_RANDOMIZE flag, and bypass the ASLR protection mechanism for a setuid or setgid program, by disabling stack-consumption resource limits.

## References
- http://www.securitytracker.com/id/1035506
- http://lists.fedoraproject.org/pipermail/package-announce/2016-April/182524.html
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00044.html
- http://www.securityfocus.com/archive/1/537996/100/0/threaded
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=8b8addf891de8a00e4d39fc32f93f7c5eb8feceb
- http://lists.opensuse.org/opensuse-security-announce/2016-06/msg00044.html
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00055.html
- http://seclists.org/fulldisclosure/2016/Apr/26
- http://hmarco.org/bugs/CVE-2016-3672-Unlimiting-the-stack-not-longer-dis
- http://hmarco.org/bugs/CVE-2016-3672-Unlimiting-the-stack-not-longer-disables-ASLR.html
- http://www.securityfocus.com/bid/85884
- https://www.exploit-db.com/exploits/39669/
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00000.html
- http://www.ubuntu.com/usn/USN-2989-1
- http://www.ubuntu.com/usn/USN-2998-1
- http://www.ubuntu.com/usn/USN-3004-1
- http://www.ubuntu.com/usn/USN-2997-1
- http://www.ubuntu.com/usn/USN-3001-1
- http://www.ubuntu.com/usn/USN-3002-1
- http://lists.opensuse.org/opensuse-security-announce/2016-06/msg00054.html
