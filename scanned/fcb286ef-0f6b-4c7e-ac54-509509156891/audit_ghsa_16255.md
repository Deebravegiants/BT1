# [C] Stimulsoft Dashboard.JS directory traversal vulnerability

## Summary
Severity: Critical
Advisory: GHSA-gfqf-9w98-7jmx
CVE: CVE-2024-24398
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2024-02-06
Source: https://github.com/advisories/GHSA-gfqf-9w98-7jmx
Type: github-advisory

## Affected
- npm: `stimulsoft-dashboards-js` — affected >=0 <2024.1.3

## Details
Directory Traversal vulnerability in Stimulsoft GmbH Stimulsoft Dashboard.JS before v.2024.1.3 allows a remote attacker to execute arbitrary code via a crafted payload to the fileName parameter of the Save function.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-24398
- https://cloud-trustit.spp.at/s/Pi78FFazHamJQ5R
- https://cves.at/posts/cve-2024-24398/writeup
- https://github.com/stimulsoft/Dashboards.JS
- http://stimulsoft.com
