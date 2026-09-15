# [C] LibreNMS before 26.8.0 Argument Injection via graph_title

## Summary
Severity: Critical
Advisory: CVE-2026-86427
Aliases: GHSA-3hvv-wxpw-cx83
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-07
Source: https://osv.dev/vulnerability/CVE-2026-86427
Type: osv

## Details
LibreNMS before 26.8.0 contains an argument injection vulnerability in the graph_title parameter that allows authenticated attackers to inject arbitrary rrdtool arguments by breaking out of double-quote escaping. Attackers can inject DEF and LINE arguments to read RRD files from unauthorized devices, or use newline injection to execute arbitrary rrdtool commands, bypassing per-device authorization checks.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/86xxx/CVE-2026-86427.json
- https://github.com/librenms/librenms/security/advisories/GHSA-3hvv-wxpw-cx83
- https://nvd.nist.gov/vuln/detail/CVE-2026-86427
- https://www.vulncheck.com/advisories/librenms-before-26.8.0-argument-injection-via-graph-title
