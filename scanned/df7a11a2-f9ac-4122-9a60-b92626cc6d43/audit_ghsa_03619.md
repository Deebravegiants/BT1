# [M] Validation bypass is possible in Json Pattern Validator

## Summary
Severity: Medium
Advisory: GHSA-rh46-3fgc-mvrf
CVE: CVE-2019-19507
CWE: CWE-287
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2019-12-04
Source: https://github.com/advisories/GHSA-rh46-3fgc-mvrf
Type: github-advisory

## Affected
- npm: `jpv` — affected >=0 <2.1.1

## Details
In jpv (aka Json Pattern Validator) before 2.1.1, compareCommon() can be bypassed because certain internal attributes can be overwritten via a conflicting name, as demonstrated by 'constructor': {'name':'Array'}. This affects validate(). Hence, a crafted payload can overwrite this builtin attribute to manipulate the type detection result.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-19507
- https://github.com/manvel-khnkoyan/jpv/issues/6
- https://www.npmjs.com/package/jpv
