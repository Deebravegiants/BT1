# [H] Seerr: Path traversal to RCE via /avatarproxy image cache filename from upstream ETag

## Summary
Severity: High
Advisory: CVE-2026-73291
Aliases: GHSA-mc6w-69r3-62h8
CVSS: 7.1 (CVSS:3.1/AV:A/AC:H/PR:N/UI:N/S:U/C:L/I:H/A:H)
Published: 2026-08-12
Source: https://osv.dev/vulnerability/CVE-2026-73291
Type: osv

## Details
Seerr is an open-source media request and discovery manager for Jellyfin, Plex, and Emby. Prior to version 3.4.0, Seerr's ImageProxy in server/lib/imageproxy.ts uses the upstream ETag and Content-Type response headers to build a cache filename for the unauthenticated GET /avatarproxy/:jellyfinUserId route, allowing a malicious or compromised Jellyfin or Emby server, or a man-in-the-middle attacker on a plaintext media-server connection, to supply traversal sequences that path.join and fs.writeFile normalize outside the cache directory, overwrite /app/dist/index.js or other files, and execute code as the node user after a container restart. This issue is fixed in version 3.4.0.

## References
- https://github.com/seerr-team/seerr/releases/tag/v3.4.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/73xxx/CVE-2026-73291.json
- https://github.com/seerr-team/seerr/security/advisories/GHSA-mc6w-69r3-62h8
- https://nvd.nist.gov/vuln/detail/CVE-2026-73291
- https://github.com/seerr-team/seerr/commit/f484791105bd81bd5404e01410431ee6fe5769c2
