# [H] Fireshare has Path Traversal Arbitrary File Write in `/api/uploadChunked`

## Summary
Severity: High
Advisory: CVE-2026-33645
Aliases: GHSA-7q8r-vpq3-89m7
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:L)
Published: 2026-03-26
Source: https://osv.dev/vulnerability/CVE-2026-33645
Type: osv

## Details
Fireshare facilitates self-hosted media and link sharing. In version 1.5.1, an authenticated path traversal vulnerability in Fireshare’s chunked upload endpoint allows an attacker to write arbitrary files outside the intended upload directory. The `checkSum` multipart field is used directly in filesystem path construction without sanitization or containment checks. This enables unauthorized file writes to attacker-chosen paths writable by the Fireshare process (e.g., container `/tmp`), violating integrity and potentially enabling follow-on attacks depending on deployment. Version 1.5.2 fixes the issue.

## References
- https://github.com/ShaneIsrael/fireshare/releases/tag/v1.5.2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33645.json
- https://github.com/ShaneIsrael/fireshare/security/advisories/GHSA-7q8r-vpq3-89m7
- https://nvd.nist.gov/vuln/detail/CVE-2026-33645
