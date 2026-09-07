# [H] Prototype Pollution in jsgui-lang-essentials

## Summary
Severity: High
Advisory: GHSA-p3pg-64pv-v7jg
CVE: CVE-2022-25301
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:H/A:H (CVSS_V3)
Published: 2022-05-03
Source: https://github.com/advisories/GHSA-p3pg-64pv-v7jg
Type: github-advisory

## Affected
- npm: `jsgui-lang-essentials` — affected >=0

## Details
All versions of package `jsgui-lang-essentials` are vulnerable to Prototype Pollution due to allowing all `Object` attributes to be altered, including their magical attributes such as `proto`, `constructor` and `prototype`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-25301
- https://github.com/metabench/jsgui-lang-essentials/issues/1
- https://github.com/metabench/jsgui-lang-essentials
- https://snyk.io/vuln/SNYK-JS-JSGUILANGESSENTIALS-2316897
