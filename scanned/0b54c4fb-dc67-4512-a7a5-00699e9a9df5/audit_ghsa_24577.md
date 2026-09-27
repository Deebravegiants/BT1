# [C] Spoon Library as used in Fork CMS allows PHP object injection

## Summary
Severity: Critical
Advisory: GHSA-2p2x-mw56-jc98
CVE: CVE-2019-15521
CWE: CWE-502
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-2p2x-mw56-jc98
Type: github-advisory

## Affected
- Packagist: `spoon/library` — affected >=0 <1.4.1

## Details
Spoon Library through 2014-02-06, as used in Fork CMS before 1.4.1 and other products, allows PHP object injection via a cookie containing an object.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-15521
- https://github.com/forkcms/library/pull/69
- https://github.com/forkcms/library
- https://github.com/forkcms/library/releases/tag/1.4.1
- https://github.com/spoon/library/blob/bda89be80b7e1ffdc93d3180d33a56927430298b/spoon/cookie/cookie.php#L117
