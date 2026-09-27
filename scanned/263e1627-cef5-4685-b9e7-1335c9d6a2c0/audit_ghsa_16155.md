# [M] Generation of Error Message Containing Sensitive Information in janeczku/calibre-web

## Summary
Severity: Medium
Advisory: GHSA-m982-h4f8-g4hf
CVE: CVE-2021-3986
CWE: CWE-209
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-11-15
Source: https://github.com/advisories/GHSA-m982-h4f8-g4hf
Type: github-advisory

## Affected
- PyPI: `calibreweb` — affected >=0 <0.6.15

## Details
A vulnerability in janeczku/calibre-web allows unauthorized users to view the names of private shelves belonging to other users. This issue occurs in the file shelf.py at line 221, where the name of the shelf is exposed in an error message when a user attempts to remove a book from a shelf they do not own. This vulnerability discloses private information and affects all versions prior to the fix.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-3986
- https://github.com/janeczku/calibre-web/commit/6f5390ead5df9779ac81fadefffb476e03f93548
- https://github.com/janeczku/calibre-web
- https://huntr.com/bounties/394af194-61a7-4e33-b373-877d4c766fca
