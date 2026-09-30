# [H] Freeswitch Denial-of-Service in SIP PUBLISH Requests via XML Entity Expansion

## Summary
Severity: High
Advisory: CVE-2026-45771
Aliases: GHSA-5vjg-pv56-vg4c
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-06-09
Source: https://osv.dev/vulnerability/CVE-2026-45771
Type: osv

## Details
FreeSWITCH is a Software Defined Telecom Stack enabling the digital transformation from proprietary telecom switches to a software implementation that runs on any commodity hardware. Prior to version 1.11.0, FreeSWITCH's bundled XML parser expands nested <!ENTITY> declarations without a depth or count bound, so a small DTD can describe a body that expands exponentially ("billion laughs"). The PIDF body of a SIP PUBLISH is fed to this parser before any digest check, letting an unauthenticated network attacker force unbounded CPU and memory consumption with a single request. This issue has been patched in version 1.11.0.

## References
- https://github.com/signalwire/freeswitch/releases/tag/v1.11.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45771.json
- https://github.com/signalwire/freeswitch/security/advisories/GHSA-5vjg-pv56-vg4c
- https://nvd.nist.gov/vuln/detail/CVE-2026-45771
