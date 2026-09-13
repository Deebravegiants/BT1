# [H] Garlic-Hub: SSRF vulnerability in uploadFromUrl endpoint

## Summary
Severity: High
Advisory: CVE-2026-47170
Aliases: GHSA-x24v-76hr-989r
CVSS: 7.7 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N)
Published: 2026-06-11
Source: https://osv.dev/vulnerability/CVE-2026-47170
Type: osv

## Details
Garlic-Hub manages digital signage network — devices, content, and playlists — from a single self-hosted interface. Prior to version 1.1, authenticated users can cause the server to issue arbitrary HTTP requests to internal services via the uploadFromUrl endpoint. This allows internal port scanning, service fingerprinting, and retrieval of internal HTTP responses which are stored in the publicly accessible media pool. This issue has been patched in version 1.1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/47xxx/CVE-2026-47170.json
- https://github.com/garlic-signage/garlic-hub/security/advisories/GHSA-x24v-76hr-989r
- https://nvd.nist.gov/vuln/detail/CVE-2026-47170
- https://github.com/garlic-signage/garlic-hub/commit/076b6d70a43d9641c35cbd8042353b473e3241f5
