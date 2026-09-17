# [M] Audiobookshelf vulnerable to Blind SSRF in `podcastUtils.js`

## Summary
Severity: Medium
Advisory: CVE-2023-51697
Aliases: GHSA-jhjx-c3wx-q2x7
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2023-12-27
Source: https://osv.dev/vulnerability/CVE-2023-51697
Type: osv

## Details
Audiobookshelf is a self-hosted audiobook and podcast server. Prior to 2.7.0, Audiobookshelf is vulnerable to unauthenticated blind server-side request (SSRF) vulnerability in `podcastUtils.js`. This vulnerability has been addressed in version 2.7.0. There are no known workarounds for this vulnerability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/51xxx/CVE-2023-51697.json
- https://github.com/advplyr/audiobookshelf/security/advisories/GHSA-jhjx-c3wx-q2x7
- https://nvd.nist.gov/vuln/detail/CVE-2023-51697
- https://github.com/advplyr/audiobookshelf/commit/f2f2ea161ca0701e1405e737b0df0f96296e4f64
