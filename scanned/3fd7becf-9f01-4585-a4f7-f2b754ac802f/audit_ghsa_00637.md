# [H] Regular Expression Denial of Service in moment

## Summary
Severity: High
Advisory: GHSA-446m-mv8f-q348
CVE: CVE-2017-18214
CWE: CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2018-03-05
Source: https://github.com/advisories/GHSA-446m-mv8f-q348
Type: github-advisory

## Affected
- npm: `moment` — affected >=0 <2.19.3

## Details
Affected versions of `moment` are vulnerable to a low severity regular expression denial of service when parsing dates as strings.


## Recommendation

Update to version 2.19.3 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-18214
- https://github.com/moment/moment/issues/4163
- https://github.com/moment/moment/pull/4326
- https://github.com/moment/moment/commit/69ed9d44957fa6ab12b73d2ae29d286a857b80eb
- https://github.com/advisories/GHSA-446m-mv8f-q348
- https://github.com/moment/moment
- https://www.npmjs.com/advisories/532
- https://www.tenable.com/security/tns-2019-02
