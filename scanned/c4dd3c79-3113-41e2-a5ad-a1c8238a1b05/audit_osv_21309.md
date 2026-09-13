# [H] CVE-2021-41991

## Summary
Severity: High
Advisory: CVE-2021-41991
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-10-18
Source: https://osv.dev/vulnerability/CVE-2021-41991
Type: osv

## Details
The in-memory certificate cache in strongSwan before 5.9.4 has a remote integer overflow upon receiving many requests with different certificates to fill the cache and later trigger the replacement of cache entries. The code attempts to select a less-often-used cache entry by means of a random number generator, but this is not done correctly. Remote code execution might be a slight possibility.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/5FJSATD2R2XHTG4P63GCMQ2N7EWKMME5/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/WQSQ3BEC22NF4NCDZVCT4P3Q2ZIAJXGJ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/Y3TQ32JLJOBJDB2EJKSX2PBPB5NFG2D4/
- https://github.com/strongswan/strongswan/releases/tag/5.9.4
- https://lists.debian.org/debian-lts-announce/2021/10/msg00014.html
- https://www.debian.org/security/2021/dsa-4989
- https://cert-portal.siemens.com/productcert/pdf/ssa-539476.pdf
- https://www.strongswan.org/blog/2021/10/18/strongswan-vulnerability-%28cve-2021-41991%29.html
