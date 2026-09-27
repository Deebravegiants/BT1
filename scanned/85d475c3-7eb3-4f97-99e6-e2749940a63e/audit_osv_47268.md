# [H] CVE-2016-1982

## Summary
Severity: High
Advisory: CVE-2016-1982
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-01-27
Source: https://osv.dev/vulnerability/CVE-2016-1982
Type: osv

## Details
The remove_chunked_transfer_coding function in filters.c in Privoxy before 3.0.24 allows remote attackers to cause a denial of service (invalid read and crash) via crafted chunk-encoded content.

## References
- http://www.openwall.com/lists/oss-security/2016/01/22/3
- http://lists.fedoraproject.org/pipermail/package-announce/2016-February/176475.html
- http://lists.fedoraproject.org/pipermail/package-announce/2016-February/176492.html
- http://www.openwall.com/lists/oss-security/2016/01/21/4
- http://www.privoxy.org/announce.txt
- http://www.debian.org/security/2016/dsa-3460
