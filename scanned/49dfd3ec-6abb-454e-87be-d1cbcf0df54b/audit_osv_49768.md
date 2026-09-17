# [H] CVE-2019-18932

## Summary
Severity: High
Advisory: CVE-2019-18932
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-01-21
Source: https://osv.dev/vulnerability/CVE-2019-18932
Type: osv

## Details
log.c in Squid Analysis Report Generator (sarg) through 2.3.11 allows local privilege escalation. By default, it uses a fixed temporary directory /tmp/sarg. As the root user, sarg creates this directory or reuses an existing one in an insecure manner. An attacker can pre-create the directory, and place symlinks in it (after winning a /tmp/sarg/denied.int_unsort race condition). The outcome will be corrupted or newly created files in privileged file system locations.

## References
- http://www.openwall.com/lists/oss-security/2020/01/20/6
- http://www.openwall.com/lists/oss-security/2020/01/27/1
- https://seclists.org/oss-sec/2020/q1/23
- https://security.gentoo.org/glsa/202007-32
- https://sourceforge.net/projects/sarg/
- http://lists.opensuse.org/opensuse-security-announce/2020-01/msg00051.html
- http://lists.opensuse.org/opensuse-security-announce/2020-01/msg00063.html
- https://bugzilla.suse.com/show_bug.cgi?id=1150554
