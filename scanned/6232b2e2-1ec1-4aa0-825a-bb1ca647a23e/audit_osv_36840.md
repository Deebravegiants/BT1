# [C] OnDemand susceptible to malicious input when navigating to a directory.

## Summary
Severity: Critical
Advisory: CVE-2026-26002
Aliases: GHSA-f83q-mhrr-3cr2
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:U)
Published: 2026-03-04
Source: https://osv.dev/vulnerability/CVE-2026-26002
Type: osv

## Details
Open OnDemand is an open-source high-performance computing portal. The Files application in OnDemand versions prior to 4.0.9 and 4.1.3 is susceptible to malicious input when navigating to a directory. This has been patched in versions 4.0.9 and 4.1.3.  Versions below this remain susceptible.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/26xxx/CVE-2026-26002.json
- https://github.com/OSC/ondemand/security/advisories/GHSA-f83q-mhrr-3cr2
- https://nvd.nist.gov/vuln/detail/CVE-2026-26002
- https://github.com/OSC/ondemand/commit/23cb167222886fdd8415277ca5c1215f4c32629c
- https://github.com/OSC/ondemand/commit/37f0ae4efb222e9c0af250feae860a720427df16
