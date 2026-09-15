# [H] frappejs was discovered to contain a prototype pollution via the function registerView

## Summary
Severity: High
Advisory: GHSA-gc7m-596h-x57r
CVE: CVE-2024-38992
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-07-01
Source: https://github.com/advisories/GHSA-gc7m-596h-x57r
Type: github-advisory

## Affected
- npm: `@airvertco/frappejs` — affected 0.0.11

## Details
airvertco frappejs v0.0.11 was discovered to contain a prototype pollution via the function registerView. This vulnerability allows attackers to execute arbitrary code or cause a Denial of Service (DoS) via injecting arbitrary properties.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-38992
- https://gist.github.com/mestrtee/10c88b9069229979ac7e52e0efc98055
- https://github.com/frappe/frappejs
- https://www.npmjs.com/package/@airvertco/frappejs
