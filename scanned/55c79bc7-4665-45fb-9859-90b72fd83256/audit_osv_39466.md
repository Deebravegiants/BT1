# [H] Penpot: Authenticated SSRF in remote image import via create-file-media-object-from-url

## Summary
Severity: High
Advisory: CVE-2026-45806
Aliases: GHSA-35g2-w7f6-8v9h
CVSS: 7.7 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N)
Published: 2026-07-15
Source: https://osv.dev/vulnerability/CVE-2026-45806
Type: osv

## Details
Penpot is an open-source design tool for design and code collaboration. Prior to 2.15.0, Penpot's remote image import passed the user-controlled url from frontend/src/app/main/data/workspace/media.cljs into the backend RPC method :create-file-media-object-from-url in backend/src/app/rpc/commands/media.clj, where media/download-image in backend/src/app/media.clj used the shared HTTP client without destination filtering, allowing an authenticated file editor to reach internal-only endpoints. This issue is fixed in version 2.15.0.

## References
- https://github.com/penpot/penpot/releases/tag/2.15.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45806.json
- https://github.com/penpot/penpot/security/advisories/GHSA-35g2-w7f6-8v9h
- https://nvd.nist.gov/vuln/detail/CVE-2026-45806
