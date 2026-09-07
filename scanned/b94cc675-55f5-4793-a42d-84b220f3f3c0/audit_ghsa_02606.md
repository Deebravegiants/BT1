# [H] Prototype Pollution in Proto

## Summary
Severity: High
Advisory: GHSA-58g2-9fqr-36q2
CVE: CVE-2021-23426
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2021-09-02
Source: https://github.com/advisories/GHSA-58g2-9fqr-36q2
Type: github-advisory

## Affected
- npm: `Proto` — affected >=0

## Details
This affects all versions of package Proto. It is possible to inject pollute the object property of an application using Proto by leveraging the merge function.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-23426
- https://github.com/adriancmiranda/Proto
- https://snyk.io/vuln/SNYK-JS-PROTO-1316301
- https://www.npmjs.com/package/Proto
