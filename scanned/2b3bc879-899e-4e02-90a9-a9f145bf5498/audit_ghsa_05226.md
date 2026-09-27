# [H] Netty has Insufficient Bailiwick Validation for NS Records

## Summary
Severity: High
Advisory: GHSA-5pvg-856g-cp85
CVE: CVE-2026-47691
CWE: CWE-345, CWE-346
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2026-06-08
Source: https://github.com/advisories/GHSA-5pvg-856g-cp85
Type: github-advisory

## Affected
- Maven: `io.netty:netty-resolver-dns` — affected >=4.2.0.Final <4.2.15.Final
- Maven: `io.netty:netty-resolver-dns` — affected >=0 <4.1.135.Final

## Details
### Summary
Netty's `DnsResolveContext` insufficiently validates the bailiwick of NS records, enabling DNS Cache Poisoning. An attacker controlling an authoritative name server for a subdomain can poison the cache for parent domains (like `.co.uk`).

### Details
In `io.netty.resolver.dns.DnsResolveContext.AuthoritativeNameServerList#add` method accepts any NS record from the AUTHORITY section as long as the record's name is a suffix of the questionName.

This means if the resolver queries evil.co.uk., it will accept an NS record claiming authority over co.uk.. Subsequently, the `handleWithAdditional` method caches the associated A records from the ADDITIONAL section directly into the `authoritativeDnsServerCache` under the parent domain's key (co.uk.). This bypasses standard bailiwick rules, where a server authoritative for a subdomain should not be trusted to provide authoritative records for its parent. The poisoned cache is then used for all future resolutions under co.uk..

The `io.netty.resolver.dns.DnsResolveContext.AuthoritativeNameServerList#cache` method only prevents caching if the record is for the root zone (dots == 1).

### Impact
DNS Cache Poisoning. Any application using Netty's DNS resolver is impacted.

## References
- https://github.com/netty/netty/security/advisories/GHSA-5pvg-856g-cp85
- https://nvd.nist.gov/vuln/detail/CVE-2026-47691
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-47691.json
- https://github.com/netty/netty/releases/tag/netty-4.2.15.Final
- https://github.com/netty/netty/releases/tag/netty-4.1.135.Final
- https://github.com/netty/netty
- https://bugzilla.redhat.com/show_bug.cgi?id=2488439
- https://access.redhat.com/security/cve/CVE-2026-47691
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
