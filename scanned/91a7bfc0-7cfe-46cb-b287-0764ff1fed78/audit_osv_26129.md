# [M] Audiobookshelf vulnerable to Blind SSRF in `Auth.js`

## Summary
Severity: Medium
Advisory: CVE-2023-51665
Aliases: GHSA-gjgj-98v3-47pg
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2023-12-27
Source: https://osv.dev/vulnerability/CVE-2023-51665
Type: osv

## Details
Audiobookshelf is a self-hosted audiobook and podcast server. Prior to 2.7.0, Audiobookshelf is vulnerable to unauthenticated blind server-side request (SSRF) vulnerability in Auth.js. This vulnerability has been addressed in version 2.7.0. There are no known workarounds for this vulnerability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/51xxx/CVE-2023-51665.json
- https://github.com/advplyr/audiobookshelf/security/advisories/GHSA-gjgj-98v3-47pg
- https://nvd.nist.gov/vuln/detail/CVE-2023-51665
- https://github.com/advplyr/audiobookshelf/commit/728496010cbfcee5b7b54001c9f79e02ede30d82
