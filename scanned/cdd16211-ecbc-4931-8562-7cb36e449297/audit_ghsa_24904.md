# [M] jwcrypto lacks the Random Filling protection mechanism

## Summary
Severity: Medium
Advisory: GHSA-wg33-x934-3ghh
CVE: CVE-2016-6298
CWE: CWE-200
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-wg33-x934-3ghh
Type: github-advisory

## Affected
- PyPI: `jwcrypto` — affected >=0 <0.3.2

## Details
The _Rsa15 class in the RSA 1.5 algorithm implementation in jwa.py in jwcrypto before 0.3.2 lacks the Random Filling protection mechanism, which makes it easier for remote attackers to obtain cleartext data via a Million Message Attack (MMA).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-6298
- https://github.com/latchset/jwcrypto/issues/65
- https://github.com/latchset/jwcrypto/pull/66
- https://github.com/latchset/jwcrypto/commit/eb5be5bd94c8cae1d7f3ba9801377084d8e5a7ba
- https://github.com/latchset/jwcrypto
- https://github.com/latchset/jwcrypto/releases/tag/v0.3.2
- https://github.com/pypa/advisory-database/tree/main/vulns/jwcrypto/PYSEC-2016-4.yaml
- https://web.archive.org/web/20200227230613/http://www.securityfocus.com/bid/92729
