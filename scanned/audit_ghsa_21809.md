# [M] Authorization Bypass Through User-Controlled Key in urijs

## Summary
Severity: Medium
Advisory: GHSA-gcv8-gh4r-25x6
CVE: CVE-2022-0613
CWE: CWE-639
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2022-02-17
Source: https://github.com/advisories/GHSA-gcv8-gh4r-25x6
Type: github-advisory

## Affected
- npm: `urijs` — affected >=0 <1.19.8

## Details
Attacker can use case-insensitive protocol schemes like HTTP, htTP, HTtp etc. in order to bypass the patch for CVE-2021-3647.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-0613
- https://github.com/medialize/uri.js/commit/6ea641cc8648b025ed5f30b090c2abd4d1a5249f
- https://github.com/medialize/uri.js
- https://huntr.dev/bounties/f53d5c42-c108-40b8-917d-9dad51535083
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/MXSSATHALUSXXD2KT6UFZAX7EG4GR332
