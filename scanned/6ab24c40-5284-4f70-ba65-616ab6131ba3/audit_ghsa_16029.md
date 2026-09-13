# [M] Improper Access Control in janeczku/calibre-web

## Summary
Severity: Medium
Advisory: GHSA-fj5v-w2jp-wqvj
CVE: CVE-2021-3987
CWE: CWE-284, CWE-862
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2024-11-15
Source: https://github.com/advisories/GHSA-fj5v-w2jp-wqvj
Type: github-advisory

## Affected
- PyPI: `calibreweb` — affected >=0 <0.6.15

## Details
An improper access control vulnerability exists in janeczku/calibre-web. The affected version allows users without public shelf permissions to create public shelves. The vulnerability is due to the `create_shelf` method in `shelf.py` not verifying if the user has the necessary permissions to create a public shelf. This issue can lead to unauthorized actions being performed by users.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-3987
- https://github.com/janeczku/calibre-web/commit/bcdc97641447965af486964537f3821f47b28874
- https://github.com/janeczku/calibre-web
- https://huntr.com/bounties/29fcc091-87b6-43bc-ab4b-3c0bec3f71df
