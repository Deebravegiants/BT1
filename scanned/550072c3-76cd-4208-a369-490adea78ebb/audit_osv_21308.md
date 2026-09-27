# [H] CVE-2021-41990

## Summary
Severity: High
Advisory: CVE-2021-41990
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-10-18
Source: https://osv.dev/vulnerability/CVE-2021-41990
Type: osv

## Details
The gmp plugin in strongSwan before 5.9.4 has a remote integer overflow via a crafted certificate with an RSASSA-PSS signature. For example, this can be triggered by an unrelated self-signed CA certificate sent by an initiator. Remote code execution cannot occur.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/5FJSATD2R2XHTG4P63GCMQ2N7EWKMME5/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/WQSQ3BEC22NF4NCDZVCT4P3Q2ZIAJXGJ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/Y3TQ32JLJOBJDB2EJKSX2PBPB5NFG2D4/
- https://cert-portal.siemens.com/productcert/pdf/ssa-539476.pdf
- https://github.com/strongswan/strongswan/releases/tag/5.9.4
- https://www.debian.org/security/2021/dsa-4989
- https://www.strongswan.org/blog/2021/10/18/strongswan-vulnerability-%28cve-2021-41990%29.html
