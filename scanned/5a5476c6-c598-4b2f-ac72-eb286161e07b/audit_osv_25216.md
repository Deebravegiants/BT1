# [H] 0-byte UDP payload DoS in c-ares

## Summary
Severity: High
Advisory: CVE-2023-32067
Aliases: GHSA-9g78-jv2r-p7vc
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-05-25
Source: https://osv.dev/vulnerability/CVE-2023-32067
Type: osv

## Details
c-ares is an asynchronous resolver library. c-ares is vulnerable to denial of service. If a target resolver sends a query, the attacker forges a malformed UDP packet with a length of 0 and returns them to the target resolver. The target resolver erroneously interprets the 0 length as a graceful shutdown of the connection. This issue has been patched in version 1.19.1.

## References
- https://github.com/c-ares/c-ares/releases/tag/cares-1_19_1
- https://lists.debian.org/debian-lts-announce/2023/06/msg00034.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/B5Z5XFNXTNPTCBBVXFDNZQVLLIE6VRBY/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/UBFWILTA33LOSV23P44FGTQQIDRJHIY7/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/32xxx/CVE-2023-32067.json
- https://github.com/c-ares/c-ares/security/advisories/GHSA-9g78-jv2r-p7vc
- https://nvd.nist.gov/vuln/detail/CVE-2023-32067
- https://security.gentoo.org/glsa/202310-09
- https://security.netapp.com/advisory/ntap-20240605-0004/
- https://www.debian.org/security/2023/dsa-5419
