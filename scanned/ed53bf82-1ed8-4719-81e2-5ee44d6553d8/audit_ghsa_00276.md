# [H] mime Regular Expression Denial of Service when MIME lookup performed on untrusted user input

## Summary
Severity: High
Advisory: GHSA-wrvr-8mpx-r7pp
CVE: CVE-2017-16138
CWE: CWE-400
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2018-07-20
Source: https://github.com/advisories/GHSA-wrvr-8mpx-r7pp
Type: github-advisory

## Affected
- npm: `mime` — affected >=2.0.0 <2.0.3
- npm: `mime` — affected >=0 <1.4.1

## Details
Affected versions of `mime` are vulnerable to regular expression denial of service when a mime lookup is performed on untrusted user input.


## Recommendation

Update to version 2.0.3 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-16138
- https://github.com/broofa/node-mime/issues/167
- https://github.com/broofa/mime/commit/1df903fdeb9ae7eaa048795b8d580ce2c98f40b0
- https://github.com/broofa/mime/commit/855d0c4b8b22e4a80b9401a81f2872058eae274d
- https://github.com/broofa/mime
