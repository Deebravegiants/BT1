# [H] hoek subject to prototype pollution via the clone function.

## Summary
Severity: High
Advisory: GHSA-c429-5p7v-vgjp
CVE: CVE-2020-36604
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-09-25
Source: https://github.com/advisories/GHSA-c429-5p7v-vgjp
Type: github-advisory

## Affected
- npm: `@hapi/hoek` — affected >=0 <8.5.1
- npm: `@hapi/hoek` — affected >=9.0.0 <9.0.3
- npm: `hoek` — affected >=0

## Details
hoek versions prior to 8.5.1, and 9.x prior to 9.0.3 are vulnerable to prototype pollution in the clone function. If an object with the __proto__ key is passed to clone() the key is converted to a prototype. This issue has been patched in version 9.0.3, and backported to 8.5.1.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-36604
- https://github.com/hapijs/hoek/issues/352
- https://github.com/hapijs/hoek/commit/4d0804bc6135ad72afdc5e1ec002b935b2f5216a
- https://github.com/hapijs/hoek/commit/948baf98634a5c206875b67d11368f133034fa90
