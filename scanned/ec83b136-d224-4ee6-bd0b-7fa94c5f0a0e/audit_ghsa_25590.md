# [H] Remote code execution in Subrion

## Summary
Severity: High
Advisory: GHSA-g54x-29xv-58h5
CVE: CVE-2021-43464
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-04-05
Source: https://github.com/advisories/GHSA-g54x-29xv-58h5
Type: github-advisory

## Affected
- Packagist: `intelliants/subrion` — affected >=0

## Details
Subrion is an open source php content management system. A Remiote Code Execution (RCE) vulnerability exiss in Subrion CMS 4.2.1 via modified code in a background field; when the information is modified, the data in it will be executed through eval().

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-43464
- https://github.com/intelliants/subrion/issues/888
- https://github.com/intelliants/subrion
