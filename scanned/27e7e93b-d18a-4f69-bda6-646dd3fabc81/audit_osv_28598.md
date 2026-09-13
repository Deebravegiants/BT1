# [M] Audiobookshelf Cross-Site-Scripting vulnerability via crafted ebooks

## Summary
Severity: Medium
Advisory: CVE-2024-35236
Aliases: GHSA-7j99-76cj-q9pg
CVSS: 4.8 (CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:L/I:L/A:N)
Published: 2024-05-27
Source: https://osv.dev/vulnerability/CVE-2024-35236
Type: osv

## Details
Audiobookshelf is a self-hosted audiobook and podcast server. Prior to version 2.10.0, opening an ebook with malicious scripts inside leads to code execution inside the browsing context. Attacking a user with high privileges (upload, creation of libraries) can lead to remote code execution (RCE) in the worst case. This was tested on version 2.9.0 on Windows, but an arbitrary file write is powerful enough as is and should easily lead to RCE on Linux, too. Version 2.10.0 contains a patch for the vulnerability.

## References
- https://github.com/advplyr/audiobookshelf/assets/36849099/46f6dfe0-9860-4ec0-a987-b3a553f7e45d
- https://github.com/advplyr/audiobookshelf/blob/04ed4810fdfcafc2e82db536edc5870e3f937d00/client/components/readers/EpubReader.vue#L319
- https://github.com/advplyr/audiobookshelf/releases/tag/v2.10.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/35xxx/CVE-2024-35236.json
- https://github.com/advplyr/audiobookshelf/security/advisories/GHSA-7j99-76cj-q9pg
- https://nvd.nist.gov/vuln/detail/CVE-2024-35236
- https://github.com/advplyr/audiobookshelf/commit/ce7f891b9b2cb57c6644aaf96f89a8bda6307664
