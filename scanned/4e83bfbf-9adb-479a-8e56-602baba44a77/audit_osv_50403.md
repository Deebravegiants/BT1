# [H] CVE-2020-15397

## Summary
Severity: High
Advisory: CVE-2020-15397
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-06-30
Source: https://osv.dev/vulnerability/CVE-2020-15397
Type: osv

## Details
HylaFAX+ through 7.0.2 and HylaFAX Enterprise have scripts that execute binaries from directories writable by unprivileged users (e.g., locations under /var/spool/hylafax that are writable by the uucp account). This allows these users to execute code in the context of the user calling these binaries (often root).

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-09/msg00054.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/J52QFVREJWJ35YSEEDDRMZQ2LM2H2WE6/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/Y46FOVJUS5SO44A2VEKR7DXEHTI4WK5L/
- http://lists.opensuse.org/opensuse-security-announce/2020-08/msg00040.html
- http://lists.opensuse.org/opensuse-security-announce/2020-08/msg00046.html
- http://lists.opensuse.org/opensuse-security-announce/2020-08/msg00039.html
- https://security.gentoo.org/glsa/202007-06
- https://bugzilla.suse.com/show_bug.cgi?id=1173519
- https://sourceforge.net/p/hylafax/HylaFAX+/2534/
