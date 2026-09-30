# [H] Suricata af-packet: defrag option can lead to truncated packets affecting visibility

## Summary
Severity: High
Advisory: CVE-2025-29915
Aliases: GHSA-7m5c-cqx4-x8mp
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2025-04-10
Source: https://osv.dev/vulnerability/CVE-2025-29915
Type: osv

## Details
Suricata is a network Intrusion Detection System, Intrusion Prevention System and Network Security Monitoring engine. The AF_PACKET defrag option is enabled by default and allows AF_PACKET to re-assemble fragmented packets before reaching Suricata. However the default packet size in Suricata is based on the network interface MTU which leads to Suricata seeing truncated packets. Upgrade to Suricata 7.0.9, which uses better defaults and adds warnings for user configurations that may lead to issues.

## References
- https://redmine.openinfosecfoundation.org/issues/5373
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/29xxx/CVE-2025-29915.json
- https://github.com/OISF/suricata/security/advisories/GHSA-7m5c-cqx4-x8mp
- https://nvd.nist.gov/vuln/detail/CVE-2025-29915
- https://github.com/OISF/suricata/commit/d78f2c9a4e2b59f44daeddff098915084493d08d
