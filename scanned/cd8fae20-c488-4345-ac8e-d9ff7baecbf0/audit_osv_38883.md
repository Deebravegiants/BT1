# [M] Audiobookshelf: Memory amplification DoS via oversized compressed details entry in backup upload

## Summary
Severity: Medium
Advisory: CVE-2026-42886
Aliases: GHSA-4jq4-rvq8-j26h
CVSS: 4.9 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-05-11
Source: https://osv.dev/vulnerability/CVE-2026-42886
Type: osv

## Details
Audiobookshelf is a self-hosted audiobook and podcast server. Prior to 2.32.2, the POST /api/backups/upload endpoint decompresses the details entry from an uploaded .audiobookshelf ZIP file entirely into memory using zip.entryData(), with no limit on the decompressed size. The upload middleware also has no file size limit. An admin user can upload a crafted ZIP containing a highly compressed details entry that, when decompressed, consumes hundreds of megabytes or gigabytes of memory, crashing the server process via out-of-memory. This vulnerability is fixed in 2.32.2.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/42xxx/CVE-2026-42886.json
- https://github.com/advplyr/audiobookshelf/security/advisories/GHSA-4jq4-rvq8-j26h
- https://nvd.nist.gov/vuln/detail/CVE-2026-42886
