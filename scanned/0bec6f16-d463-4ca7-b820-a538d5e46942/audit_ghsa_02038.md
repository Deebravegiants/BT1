# [H] Uncontrolled Resource Consumption in locutus

## Summary
Severity: High
Advisory: GHSA-39q4-p535-c852
CVE: CVE-2021-23392
CWE: CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-06-10
Source: https://github.com/advisories/GHSA-39q4-p535-c852
Type: github-advisory

## Affected
- npm: `locutus` — affected >=0 <2.0.15

## Details
The package locutus before 2.0.15 is vulnerable to Regular Expression Denial of Service (ReDoS) via the gopher_parsedir function.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-23392
- https://github.com/locutusjs/locutus/pull/446
- https://github.com/locutusjs/locutus/commit/eb863321990e7e5514aa14f68b8d9978ece9e65e
- https://snyk.io/vuln/SNYK-JS-LOCUTUS-1090597
