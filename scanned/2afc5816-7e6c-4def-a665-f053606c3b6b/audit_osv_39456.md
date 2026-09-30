# [H] Suricata lua: excessive flow variable registration can bypass sandbox

## Summary
Severity: High
Advisory: CVE-2026-45770
Aliases: GHSA-653j-cc95-vj4c
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2026-09-10
Source: https://osv.dev/vulnerability/CVE-2026-45770
Type: osv

## Details
Suricata is a network Intrusion Detection System, Intrusion Prevention System and Network Security Monitoring engine. Starting in version 8.0.0 and prior to version 8.0.5, a Lua rule that registers too many flow variables can corrupt Lua detection state and may bypass Suricata's restricted Lua sandbox. This requires an affected Lua script/rule to be loaded. Excessive flow variables being registered may also cause Suricata to crash. Version 8.0.5 contains a fix. As a workaround, disable `security.lua.allow-rules` unless Lua rules are required.

## References
- https://forum.suricata.io/t/suricata-8-0-5-and-7-0-16-released/6315
- https://redmine.openinfosecfoundation.org/issues/8556
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45770.json
- https://github.com/OISF/suricata/security/advisories/GHSA-653j-cc95-vj4c
- https://nvd.nist.gov/vuln/detail/CVE-2026-45770
