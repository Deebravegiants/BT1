# [C] OpenS100 Portrayal Engine Unrestricted Lua Standard Library Access

## Summary
Severity: Critical
Advisory: CVE-2026-22208
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:A/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2026-02-17
Source: https://osv.dev/vulnerability/CVE-2026-22208
Type: osv

## Details
OpenS100 (the reference implementation S-100 viewer) prior to commit 753cf29 contains a remote code execution vulnerability via an unrestricted Lua interpreter. The Portrayal Engine initializes Lua using luaL_openlibs() without sandboxing or capability restrictions, exposing standard libraries such as 'os' and 'io' to untrusted portrayal catalogues. An attacker can provide a malicious S-100 portrayal catalogue containing Lua scripts that execute arbitrary commands with the privileges of the OpenS100 process when a user imports the catalogue and loads a chart.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/22xxx/CVE-2026-22208.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-22208
- https://www.vulncheck.com/advisories/opens100-portrayal-engine-unrestricted-lua-standard-library-access
- https://github.com/S-100ExpertTeam/OpenS100/commit/753cf294434e8d3961f20a567c4d99151e3b530d
- https://github.com/S-100ExpertTeam/OpenS100
- https://www.mdpi.com/1424-8220/26/4/1246
