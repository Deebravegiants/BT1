# [H] Subrion CMS CSRF Vulnerability

## Summary
Severity: High
Advisory: GHSA-g8j7-w673-4mjp
CVE: CVE-2018-21037
CWE: CWE-352
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-g8j7-w673-4mjp
Type: github-advisory

## Affected
- Packagist: `intelliants/subrion` — affected >=0 <4.2.1

## Details
Subrion CMS 4.1.5 (and possibly earlier versions) allow CSRF to change the administrator password via the `panel/members/edit/1` URI.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-21037
- https://github.com/intelliants/subrion/issues/638
- https://github.com/intelliants/subrion
- https://github.com/intelliants/subrion/blob/c8aaeb04f44554e454be9763527a7be7fbe7bfd5/changelog.txt#L899
