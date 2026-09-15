# [M] CVE-2020-10732

## Summary
Severity: Medium
Advisory: CVE-2020-10732
Aliases: A-170658976, ASB-A-170658976
CVSS: 4.4 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:L)
Published: 2020-06-12
Source: https://osv.dev/vulnerability/CVE-2020-10732
Type: osv

## Details
A flaw was found in the Linux kernel's implementation of Userspace core dumps. This flaw allows an attacker with a local account to crash a trivial program and exfiltrate private kernel data.

## References
- https://lore.kernel.org/lkml/CAG_fn=VZZ7yUxtOGzuTLkr7wmfXWtKK9BHHYawj=rt9XWnCYvg%40mail.gmail.com/
- https://security.netapp.com/advisory/ntap-20210129-0005/
- https://usn.ubuntu.com/4411-1/
- https://usn.ubuntu.com/4440-1/
- https://usn.ubuntu.com/4485-1/
- http://lists.opensuse.org/opensuse-security-announce/2020-06/msg00022.html
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00008.html
- https://twitter.com/grsecurity/status/1252558055629299712
- https://usn.ubuntu.com/4427-1/
- https://usn.ubuntu.com/4439-1/
- https://github.com/google/kmsan/issues/76
- https://git.kernel.org/pub/scm/linux/kernel/git/next/linux-next.git/commit/?id=aca969cacf07f41070d788ce2b8ca71f09d5207d
- https://github.com/ruscur/linux/commit/a95cdec9fa0c08e6eeb410d461c03af8fd1fef0a
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2020-10732
