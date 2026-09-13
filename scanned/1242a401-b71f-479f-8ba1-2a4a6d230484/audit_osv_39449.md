# [M] Suricata lua: sandbox allocation limit not enforced for new allocations

## Summary
Severity: Medium
Advisory: CVE-2026-45763
Aliases: GHSA-9h43-frr8-xx6m
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-09-10
Source: https://osv.dev/vulnerability/CVE-2026-45763
Type: osv

## Details
Suricata is a network Intrusion Detection System, Intrusion Prevention System and Network Security Monitoring engine. Starting in version 8.0.0 and prior to version 8.0.5, when Lua rule execution is enabled, the Lua sandbox memory limit was not consistently enforced for new allocations. Certain Lua allocation patterns could exceed `security.lua.max-bytes` without triggering the intended memory limit, making the configured sandbox limit unreliable. This requires Lua rules to be enabled and an affected Lua script/rule to be loaded. Version 8.0.5 contains a fix. As a workaround, disable `security.lua.allow-rules` unless Lua rules are required.

## References
- https://forum.suricata.io/t/suricata-8-0-5-and-7-0-16-released/6315
- https://redmine.openinfosecfoundation.org/issues/8507
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45763.json
- https://github.com/OISF/suricata/security/advisories/GHSA-9h43-frr8-xx6m
- https://nvd.nist.gov/vuln/detail/CVE-2026-45763
