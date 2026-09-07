# [H] Injection and Cross-site Scripting in osm-static-maps

## Summary
Severity: High
Advisory: GHSA-pxcf-v868-m492
CVE: CVE-2020-7749
CWE: CWE-74, CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:L (CVSS_V3)
Published: 2021-05-10
Source: https://github.com/advisories/GHSA-pxcf-v868-m492
Type: github-advisory

## Affected
- npm: `osm-static-maps` — affected >=0 <3.9.0

## Details
This affects all versions of package osm-static-maps under 3.9.0. User input given to the package is passed directly to a template without escaping `({{{ ... }}})`. As such, it is possible for an attacker to inject arbitrary HTML/JS code and depending on the context. It will be outputted as an HTML on the page which gives opportunity for XSS or rendered on the server (puppeteer) which also gives opportunity for SSRF and Local File Read.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7749
- https://github.com/jperelli/osm-static-maps/pull/24
- https://github.com/jperelli/osm-static-maps/commit/97355d29e08753d1cfe99b1281dbaa06f4e651b0
- https://github.com/jperelli/osm-static-maps/blob/master/src/template.html%23L142
- https://snyk.io/vuln/SNYK-JS-OSMSTATICMAPS-609637
