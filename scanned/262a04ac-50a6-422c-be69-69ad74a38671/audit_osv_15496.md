# [H] CVE-2019-16866

## Summary
Severity: High
Advisory: CVE-2019-16866
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-10-03
Source: https://osv.dev/vulnerability/CVE-2019-16866
Type: osv

## Details
Unbound before 1.9.4 accesses uninitialized memory, which allows remote attackers to trigger a crash via a crafted NOTIFY query. The source IP address of the query must match an access-control rule.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/E65NCWZZB2D75ZIYWPXKMVGSGNYW4JMC/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/MLRHE7TQFAOV4MB2ELTOGESZYUL65NUJ/
- https://seclists.org/bugtraq/2019/Oct/23
- https://github.com/NLnetLabs/unbound/blob/release-1.9.4/doc/Changelog
- https://usn.ubuntu.com/4149-1/
- https://www.debian.org/security/2019/dsa-4544
- https://nlnetlabs.nl/downloads/unbound/CVE-2019-16866.txt
