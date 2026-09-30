# [M] Reverse Tabnabbing in quill

## Summary
Severity: Medium
Advisory: GHSA-588m-9qg5-35pq
CWE: CWE-1022
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2020-09-03
Source: https://github.com/advisories/GHSA-588m-9qg5-35pq
Type: github-advisory

## Affected
- npm: `quill` — affected >=0 <1.3.7

## Details
Versions of `quill` prior to 1.3.7 are vulnerable to [Reverse Tabnabbing](https://www.owasp.org/index.php/Reverse_Tabnabbing). The package uses `target='_blank'` in anchor tags, allowing attackers to access `window.opener` for the original page when opening links. This is commonly used for phishing attacks.


## Recommendation

No fix is currently available. Consider using an alternative package until a fix is made available.

## References
- https://github.com/quilljs/quill/issues/2438
- https://github.com/quilljs/quill/pull/2674
- https://github.com/quilljs/quill
- https://www.npmjs.com/advisories/1039
