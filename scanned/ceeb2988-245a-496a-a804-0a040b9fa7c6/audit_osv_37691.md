# [M] Squid has Denial of Service in ICP Response handling

## Summary
Severity: Medium
Advisory: CVE-2026-32748
Aliases: GHSA-f9p7-3jqg-hhvq
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:L)
Published: 2026-03-26
Source: https://osv.dev/vulnerability/CVE-2026-32748
Type: osv

## Details
Squid is a caching proxy for the Web. Prior to version 7.5, due to premature release of resource during expected lifetime and heap Use-After-Free bugs, Squid is vulnerable to Denial of Service when handling ICP traffic. This problem allows a remote attacker to perform a reliable and repeatable Denial of Service attack against the Squid service using ICP protocol. This attack is limited to Squid deployments that explicitly enable ICP support (i.e. configure non-zero `icp_port`). This problem _cannot_ be mitigated by denying ICP queries using `icp_access` rules. This bug is fixed in Squid version 7.5.

## References
- http://www.openwall.com/lists/oss-security/2026/03/25/3
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-32748.json
- https://access.redhat.com/errata/RHSA-2026:10255
- https://access.redhat.com/errata/RHSA-2026:10256
- https://access.redhat.com/errata/RHSA-2026:10257
- https://access.redhat.com/errata/RHSA-2026:11901
- https://access.redhat.com/errata/RHSA-2026:20564
- https://access.redhat.com/errata/RHSA-2026:20565
- https://access.redhat.com/errata/RHSA-2026:20580
- https://access.redhat.com/errata/RHSA-2026:6301
- https://access.redhat.com/errata/RHSA-2026:8119
- https://access.redhat.com/errata/RHSA-2026:8317
- https://access.redhat.com/errata/RHSA-2026:8880
- https://access.redhat.com/errata/RHSA-2026:9220
- https://access.redhat.com/security/cve/CVE-2026-32748
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/32xxx/CVE-2026-32748.json
- https://github.com/squid-cache/squid/security/advisories/GHSA-f9p7-3jqg-hhvq
- https://nvd.nist.gov/vuln/detail/CVE-2026-32748
- https://bugzilla.redhat.com/show_bug.cgi?id=2451577
- https://github.com/squid-cache/squid/commit/703e07d25ca6fa11f52d20bf0bb879e22ab7481b
