# [M] Squid vulnerable to Denial of Service in ICP Request handling

## Summary
Severity: Medium
Advisory: CVE-2026-33526
Aliases: GHSA-hpfx-h48q-gvwg
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:H)
Published: 2026-03-26
Source: https://osv.dev/vulnerability/CVE-2026-33526
Type: osv

## Details
Squid is a caching proxy for the Web. Prior to version 7.5, due to heap Use-After-Free, Squid is vulnerable to Denial of Service when handling ICP traffic. This problem allows a remote attacker to perform a reliable and repeatable Denial of Service attack against the Squid service using ICP protocol. This attack is limited to Squid deployments that explicitly enable ICP support (i.e. configure non-zero `icp_port`). This problem _cannot_ be mitigated by denying ICP queries using `icp_access` rules. Version 7.5 contains a patch.

## References
- http://www.openwall.com/lists/oss-security/2026/03/25/2
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-33526.json
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
- https://access.redhat.com/security/cve/CVE-2026-33526
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33526.json
- https://github.com/squid-cache/squid/security/advisories/GHSA-hpfx-h48q-gvwg
- https://nvd.nist.gov/vuln/detail/CVE-2026-33526
- https://bugzilla.redhat.com/show_bug.cgi?id=2451574
- https://github.com/squid-cache/squid/commit/8a7d42f9d44befb8fcbbb619505587c8de6a1e91
