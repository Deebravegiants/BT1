# [C] ts-deepmerge before 2.0.2 vulnerable to Prototype Pollution

## Summary
Severity: Critical
Advisory: GHSA-7qqq-gh2f-wq76
CVE: CVE-2022-25907
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-08-10
Source: https://github.com/advisories/GHSA-7qqq-gh2f-wq76
Type: github-advisory

## Affected
- npm: `ts-deepmerge` — affected >=0 <2.0.2

## Details
The package ts-deepmerge before version 2.0.2 is vulnerable to Prototype Pollution due to missing sanitization of the `merge` function.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-25907
- https://github.com/voodoocreation/ts-deepmerge/commit/9be5148773343c57be9de39728d6ead18eddf10b
- https://github.com/voodoocreation/ts-deepmerge
- https://github.com/voodoocreation/ts-deepmerge/releases/tag/2.0.2
- https://security.snyk.io/vuln/SNYK-JS-TSDEEPMERGE-2959975
