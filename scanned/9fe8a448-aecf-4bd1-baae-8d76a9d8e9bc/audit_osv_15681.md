# [M] CVE-2019-18677

## Summary
Severity: Medium
Advisory: CVE-2019-18677
CVSS: 6.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N)
Published: 2019-11-26
Source: https://osv.dev/vulnerability/CVE-2019-18677
Type: osv

## Details
An issue was discovered in Squid 3.x and 4.x through 4.8 when the append_domain setting is used (because the appended characters do not properly interact with hostname length restrictions). Due to incorrect message processing, it can inappropriately redirect traffic to origins it should not be delivered to.

## References
- https://lists.debian.org/debian-lts-announce/2020/07/msg00009.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/MTM74TU2BSLT5B3H4F3UDW53672NVLMC/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/UEMOYTMCCFWK5NOXSXEIH5D2VGWVXR67/
- http://www.squid-cache.org/Advisories/SQUID-2019_9.txt
- http://www.squid-cache.org/Versions/v3/3.5/changesets/squid-3.5-e5f1813a674848dde570f7920873e1071f96e0b4.patch
- http://www.squid-cache.org/Versions/v4/changesets/squid-4-36492033ea4097821a4f7ff3ddcb971fbd1e8ba0.patch
- https://lists.debian.org/debian-lts-announce/2019/12/msg00011.html
- https://usn.ubuntu.com/4213-1/
- https://www.debian.org/security/2020/dsa-4682
- https://bugzilla.suse.com/show_bug.cgi?id=1156328
- https://github.com/squid-cache/squid/pull/427
