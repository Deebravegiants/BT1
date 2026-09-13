# [M] Prototype pollution in class-transformer

## Summary
Severity: Medium
Advisory: GHSA-6gp3-h3jj-prx4
CVE: CVE-2020-7637
CWE: CWE-1321, CWE-915
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2020-04-07
Source: https://github.com/advisories/GHSA-6gp3-h3jj-prx4
Type: github-advisory

## Affected
- npm: `class-transformer` — affected >=0 <0.3.1

## Details
class-transformer through 0.2.3 is vulnerable to Prototype Pollution. The 'classToPlainFromExist' function could be tricked into adding or modifying properties of 'Object.prototype' using a '__proto__' payload.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7637
- https://github.com/typestack/class-transformer/commit/8f04eb9db02de708f1a20f6f2d2bb309b2fed01e
- https://github.com/typestack/class-transformer
- https://github.com/typestack/class-transformer/blob/a650d9f490573443f62508bc063b857bcd5e2525/src/ClassTransformer.ts#L29-L31,
- https://snyk.io/vuln/SNYK-JS-CLASSTRANSFORMER-564431
