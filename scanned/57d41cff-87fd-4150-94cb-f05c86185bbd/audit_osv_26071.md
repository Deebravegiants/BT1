# [H] CVE-2023-50387

## Summary
Severity: High
Advisory: CVE-2023-50387
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-02-14
Source: https://osv.dev/vulnerability/CVE-2023-50387
Type: osv

## Details
Certain DNSSEC aspects of the DNS protocol (in RFC 4033, 4034, 4035, 6840, and related RFCs) allow remote attackers to cause a denial of service (CPU consumption) via one or more DNSSEC responses, aka the "KeyTrap" issue. One of the concerns is that, when there is a zone with many DNSKEY and RRSIG records, the protocol specification implies that an algorithm must evaluate all combinations of DNSKEY and RRSIG records.

## References
- https://access.redhat.com/security/cve/CVE-2023-50387
- https://gitlab.nic.cz/knot/knot-resolver/-/releases/v5.7.1
- https://kb.isc.org/docs/cve-2023-50387
- https://lists.debian.org/debian-lts-announce/2024/09/msg00001.html
- https://lists.debian.org/debian-lts-announce/2024/11/msg00035.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/BUIP7T7Z4T3UHLXFWG6XIVDP4GYPD3AI/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/HVRDSJVZKMCXKKPP6PNR62T7RWZ3YSDZ/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/RGS7JN6FZXUSTC2XKQHH27574XOULYYJ/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/ZDZFMEKQTZ4L7RY46FCENWFB5MDT263R/
- https://lists.thekelleys.org.uk/pipermail/dnsmasq-discuss/2024q1/017430.html
- https://msrc.microsoft.com/update-guide/vulnerability/CVE-2023-50387
- https://news.ycombinator.com/item?id=39367411
- https://news.ycombinator.com/item?id=39372384
- https://nlnetlabs.nl/news/2024/Feb/13/unbound-1.19.1-released/
- https://www.athene-center.de/aktuelles/key-trap
- https://www.athene-center.de/fileadmin/content/PDF/Technical_Report_KeyTrap.pdf
- https://www.securityweek.com/keytrap-dns-attack-could-disable-large-parts-of-internet-researchers/
- https://www.theregister.com/2024/02/13/dnssec_vulnerability_internet/
- https://docs.powerdns.com/recursor/security-advisories/powerdns-advisory-2024-01.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/50xxx/CVE-2023-50387.json
