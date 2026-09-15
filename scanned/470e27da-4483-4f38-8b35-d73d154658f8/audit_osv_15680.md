# [H] CVE-2019-18676

## Summary
Severity: High
Advisory: CVE-2019-18676
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-11-26
Source: https://osv.dev/vulnerability/CVE-2019-18676
Type: osv

## Details
An issue was discovered in Squid 3.x and 4.x through 4.8. Due to incorrect input validation, there is a heap-based buffer overflow that can result in Denial of Service to all clients using the proxy. Severity is high due to this vulnerability occurring before normal security checks; any remote client that can reach the proxy port can trivially perform the attack via a crafted URI scheme.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/MTM74TU2BSLT5B3H4F3UDW53672NVLMC/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/UEMOYTMCCFWK5NOXSXEIH5D2VGWVXR67/
- http://www.squid-cache.org/Advisories/SQUID-2019_8.txt
- https://lists.debian.org/debian-lts-announce/2020/07/msg00009.html
- https://usn.ubuntu.com/4213-1/
- https://usn.ubuntu.com/4446-1/
- https://www.debian.org/security/2020/dsa-4682
- https://bugzilla.suse.com/show_bug.cgi?id=1156329
- http://www.squid-cache.org/Versions/v4/changesets/squid-4-fbbdf75efd7a5cc244b4886a9d42ea458c5a3a73.patch
- https://github.com/squid-cache/squid/pull/275
