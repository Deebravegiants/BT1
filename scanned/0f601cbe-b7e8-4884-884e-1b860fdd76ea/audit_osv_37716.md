# [H] PJSIP is vulnerable to Heap-based Buffer Overflow through DNS parser

## Summary
Severity: High
Advisory: CVE-2026-32945
Aliases: GHSA-jr2p-p2w4-rr9q
CVSS: 7.5 (CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:N/VC:H/VI:L/VA:H/SC:N/SI:N/SA:N)
Published: 2026-03-20
Source: https://osv.dev/vulnerability/CVE-2026-32945
Type: osv

## Details
PJSIP is a free and open source multimedia communication library written in C. Versions 2.16 and below have a Heap-based Buffer Overflowvulnerability in the DNS parser's name length handler. Thisimpacts applications using PJSIP's built-in DNS resolver, such as those configured with pjsua_config.nameserver or UaConfig.nameserver in PJSUA/PJSUA2. It does not affect users who rely on the OS resolver (e.g., getaddrinfo()) by not configuring a nameserver, or those using an external resolver via pjsip_resolver_set_ext_resolver(). This issue is fixed in version 2.17. For users unable to upgrade, a workaround is to disable DNS resolution in the PJSIP config (by setting nameserver_count to zero) or to use an external resolver implementation instead.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/32xxx/CVE-2026-32945.json
- https://github.com/pjsip/pjproject/security/advisories/GHSA-jr2p-p2w4-rr9q
- https://nvd.nist.gov/vuln/detail/CVE-2026-32945
- https://github.com/pjsip/pjproject/commit/5311aee398ae9d623829a6bad7b679a193c9e199
