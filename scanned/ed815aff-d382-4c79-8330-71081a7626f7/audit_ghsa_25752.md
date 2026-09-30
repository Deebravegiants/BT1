# [M] Prototype Pollution in bodymen

## Summary
Severity: Medium
Advisory: GHSA-vhxc-fhm5-qcp9
CVE: CVE-2022-25296
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2022-03-18
Source: https://github.com/advisories/GHSA-vhxc-fhm5-qcp9
Type: github-advisory

## Affected
- npm: `bodymen` — affected >=0.0.0

## Details
The package bodymen from 0.0.0 are vulnerable to Prototype Pollution via the handler function which could be tricked into adding or modifying properties of Object.prototype using a __proto__ payload. **Note:** This vulnerability derives from an incomplete fix to [CVE-2019-10792](https://security.snyk.io/vuln/SNYK-JS-BODYMEN-548897)

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-25296
- https://github.com/diegohaz/bodymen
- https://snyk.io/vuln/SNYK-JS-BODYMEN-2342623
