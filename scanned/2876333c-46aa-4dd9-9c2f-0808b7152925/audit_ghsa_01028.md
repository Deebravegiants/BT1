# [C] Path Traversal in decompress

## Summary
Severity: Critical
Advisory: GHSA-qgfr-5hqp-vrw9
CVE: CVE-2020-12265
CWE: CWE-22, CWE-59
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2020-09-03
Source: https://github.com/advisories/GHSA-qgfr-5hqp-vrw9
Type: github-advisory

## Affected
- npm: `decompress` — affected >=0 <4.2.1

## Details
Versions of `decompress` prior to 4.2.1 are vulnerable to Arbitrary File Write. The package fails to prevent extraction of files with relative paths, allowing attackers to write to any folder in the system by including filenames containing`../`.


## Recommendation

Upgrade to version 4.2.1 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-12265
- https://github.com/kevva/decompress/issues/71
- https://github.com/kevva/decompress/pull/73
- https://github.com/kevva/decompress/commit/967146e70f48be32ed1a69daa3941d681944d513
- https://github.com/kevva/decompress
