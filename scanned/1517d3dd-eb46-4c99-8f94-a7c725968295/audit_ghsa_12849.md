# [C] kelvinmo simplexrd vulnerable to Improper Restriction of XML External Entity Reference

## Summary
Severity: Critical
Advisory: GHSA-rh3m-pr36-xh2f
CVE: CVE-2015-10029
CWE: CWE-611
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-01-07
Source: https://github.com/advisories/GHSA-rh3m-pr36-xh2f
Type: github-advisory

## Affected
- Packagist: `kelvinmo/simplexrd` — affected >=0 <3.1.1

## Details
A vulnerability classified as problematic was found in kelvinmo simplexrd up to 3.1.0. This vulnerability affects unknown code of the file `simplexrd/simplexrd.class.php`. The manipulation leads to xml external entity reference. Upgrading to version 3.1.1 is able to address this issue. The name of the patch is 4c9f2e028523ed705b555eca2c18c64e71f1a35d. It is recommended to upgrade the affected component. VDB-217630 is the identifier assigned to this vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-10029
- https://github.com/kelvinmo/simplexrd/commit/4c9f2e028523ed705b555eca2c18c64e71f1a35d
- https://github.com/kelvinmo/simplexrd
- https://github.com/kelvinmo/simplexrd/releases/tag/v3.1.1
- https://vuldb.com/?ctiid.217630
- https://vuldb.com/?id.217630
