# [M] CVE-2015-8575

## Summary
Severity: Medium
Advisory: CVE-2015-8575
CVSS: 4.0 (CVSS:3.0/AV:L/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2016-02-08
Source: https://osv.dev/vulnerability/CVE-2015-8575
Type: osv

## Details
The sco_sock_bind function in net/bluetooth/sco.c in the Linux kernel before 4.3.4 does not verify an address length, which allows local users to obtain sensitive information from kernel memory and bypass the KASLR protection mechanism via a crafted application.

## References
- http://www.debian.org/security/2016/dsa-3434
- http://www.ubuntu.com/usn/USN-2886-1
- http://www.ubuntu.com/usn/USN-2888-1
- http://www.ubuntu.com/usn/USN-2890-1
- http://www.ubuntu.com/usn/USN-2890-2
- http://www.ubuntu.com/usn/USN-2890-3
- https://github.com/torvalds/linux/commit/5233252fce714053f0151680933571a2da9cbfb4
- https://bugzilla.redhat.com/show_bug.cgi?id=1292840
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=5233252fce714053f0151680933571a2da9cbfb4
- http://lists.fedoraproject.org/pipermail/package-announce/2016-February/176484.html
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00094.html
- http://lists.opensuse.org/opensuse-security-announce/2016-04/msg00045.html
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00038.html
- http://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.3.4
- http://www.openwall.com/lists/oss-security/2015/12/16/3
- http://www.securityfocus.com/bid/79724
