# [H] CVE-2020-7040

## Summary
Severity: High
Advisory: CVE-2020-7040
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-01-21
Source: https://osv.dev/vulnerability/CVE-2020-7040
Type: osv

## Details
storeBackup.pl in storeBackup through 3.5 relies on the /tmp/storeBackup.lock pathname, which allows symlink attacks that possibly lead to privilege escalation. (Local users can also create a plain file named /tmp/storeBackup.lock to block use of storeBackup until an admin manually deletes that file.)

## References
- https://lists.debian.org/debian-lts-announce/2020/02/msg00003.html
- https://usn.ubuntu.com/4508-1/
- http://www.openwall.com/lists/oss-security/2020/01/20/3
- http://www.openwall.com/lists/oss-security/2020/01/21/2
- http://www.openwall.com/lists/oss-security/2020/01/22/2
- http://www.openwall.com/lists/oss-security/2020/01/22/3
- http://www.openwall.com/lists/oss-security/2020/01/23/1
- https://seclists.org/oss-sec/2020/q1/20
- https://bugzilla.suse.com/show_bug.cgi?id=CVE-2020-7040
- http://lists.opensuse.org/opensuse-security-announce/2020-01/msg00054.html
