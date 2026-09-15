# [H] Netty Vulnerable to DNS Cache Poisoning via Missing Bailiwick Checks in CNAME Records

## Summary
Severity: High
Advisory: GHSA-676x-f7gg-47vc
CVE: CVE-2026-45674
CWE: CWE-345, CWE-346
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2026-06-08
Source: https://github.com/advisories/GHSA-676x-f7gg-47vc
Type: github-advisory

## Affected
- Maven: `io.netty:netty-resolver-dns` — affected >=4.2.0.Final <4.2.15.Final
- Maven: `io.netty:netty-resolver-dns` — affected >=0 <4.1.135.Final

## Details
### Summary
Netty's DnsResolveContext fails to validate the origin (bailiwick) of CNAME records in DNS responses.

### Details
In `io.netty.resolver.dns.DnsResolveContext#buildAliasMap`, the resolver processes the ANSWER section of a DNS response and blindly caches all CNAME records it finds.

According to https://datatracker.ietf.org/doc/html/rfc5452#section-6 

```
Care must be taken to only accept
   data if it is known that the originator is authoritative for the
   QNAME or a parent of the QNAME.
   One very simple way to achieve this is to only accept data if it is
   part of the domain for which the query was intended.
```

### Impact
DNS Cache Poisoning (Bailiwick Bypass). Any application using Netty's DNS resolver is impacted.

## References
- https://github.com/netty/netty/security/advisories/GHSA-676x-f7gg-47vc
- https://nvd.nist.gov/vuln/detail/CVE-2026-45674
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-45674.json
- https://github.com/netty/netty/releases/tag/netty-4.2.15.Final
- https://github.com/netty/netty/releases/tag/netty-4.1.135.Final
- https://github.com/netty/netty
- https://bugzilla.redhat.com/show_bug.cgi?id=2488400
- https://access.redhat.com/security/cve/CVE-2026-45674
- https://access.redhat.com/errata/RHSA-2026:62260
- https://access.redhat.com/errata/RHSA-2026:54435
- https://access.redhat.com/errata/RHSA-2026:53806
- https://access.redhat.com/errata/RHSA-2026:53644
- https://access.redhat.com/errata/RHSA-2026:50085
- https://access.redhat.com/errata/RHSA-2026:49701
- https://access.redhat.com/errata/RHSA-2026:49700
- https://access.redhat.com/errata/RHSA-2026:48151
- https://access.redhat.com/errata/RHSA-2026:41951
- https://access.redhat.com/errata/RHSA-2026:37390
- https://access.redhat.com/errata/RHSA-2026:34608
- https://access.redhat.com/errata/RHSA-2026:26586
