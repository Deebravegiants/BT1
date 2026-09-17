# [H] Denial of Service in yar

## Summary
Severity: High
Advisory: GHSA-gg6m-fhqv-hg56
CVE: CVE-2014-4179
CWE: CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2020-09-01
Source: https://github.com/advisories/GHSA-gg6m-fhqv-hg56
Type: github-advisory

## Affected
- npm: `yar` — affected >=0 <2.2.0

## Details
Versions of `yar` prior to 2.2.0 are affected by a denial of service vulnerability related to an invalid encrypted session cookie value.

When an invalid encryped session cookie value is provided, the process will crash.


## Recommendation

Update to version 2.2.0 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-4179
- https://github.com/spumko/yar/issues/34
- https://github.com/spumko/yar
- https://www.npmjs.com/advisories/44
