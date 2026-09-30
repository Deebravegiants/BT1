# [M] Injection in bodymen

## Summary
Severity: Medium
Advisory: GHSA-8h84-8j4f-p97q
CVE: CVE-2019-10792
CWE: CWE-74
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2021-04-13
Source: https://github.com/advisories/GHSA-8h84-8j4f-p97q
Type: github-advisory

## Affected
- npm: `bodymen` — affected >=0 <1.1.1

## Details
bodymen before 1.1.1 is vulnerable to Prototype Pollution. The handler function could be tricked into adding or modifying properties of Object.prototype using a __proto__ payload.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10792
- https://github.com/diegohaz/bodymen/commit/5d52e8cf360410ee697afd90937e6042c3a8653b
- https://snyk.io/vuln/SNYK-JS-BODYMEN-548897
