# [H] CVE-2023-50868

## Summary
Severity: High
Advisory: CVE-2023-50868
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2024-02-14
Source: https://osv.dev/vulnerability/CVE-2023-50868
Type: osv

## Details
The Closest Encloser Proof aspect of the DNS protocol (in RFC 5155 when RFC 9276 guidance is skipped) allows remote attackers to cause a denial of service (CPU consumption for SHA-1 computations) via DNSSEC responses in a random subdomain attack, aka the "NSEC3" issue. The RFC 5155 specification implies that an algorithm must perform thousands of iterations of a hash function in certain situations.

## References
- https://access.redhat.com/security/cve/CVE-2023-50868
- https://datatracker.ietf.org/doc/html/rfc5155
- https://gitlab.nic.cz/knot/knot-resolver/-/releases/v5.7.1
- https://kb.isc.org/docs/cve-2023-50868
- https://lists.debian.org/debian-lts-announce/2024/09/msg00001.html
- https://lists.debian.org/debian-lts-announce/2024/11/msg00035.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/BUIP7T7Z4T3UHLXFWG6XIVDP4GYPD3AI/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/HVRDSJVZKMCXKKPP6PNR62T7RWZ3YSDZ/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/ZDZFMEKQTZ4L7RY46FCENWFB5MDT263R/
- https://lists.thekelleys.org.uk/pipermail/dnsmasq-discuss/2024q1/017430.html
- https://nlnetlabs.nl/news/2024/Feb/13/unbound-1.19.1-released/
- https://docs.powerdns.com/recursor/security-advisories/powerdns-advisory-2024-01.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/50xxx/CVE-2023-50868.json
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/6FV5O347JTX7P5OZA6NGO4MKTXRXMKOZ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/BUIP7T7Z4T3UHLXFWG6XIVDP4GYPD3AI/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/HVRDSJVZKMCXKKPP6PNR62T7RWZ3YSDZ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/IGSLGKUAQTW5JPPZCMF5YPEYALLRUZZ6/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/PNNHZSZPG2E7NBMBNYPGHCFI4V4XRWNQ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/RGS7JN6FZXUSTC2XKQHH27574XOULYYJ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/SVYA42BLXUCIDLD35YIJPJSHDIADNYMP/
