# [H] Checkmate: Pre-auth Denial of Service via File Upload on Registration

## Summary
Severity: High
Advisory: CVE-2026-55241
Aliases: GHSA-9xvg-x28f-m78m
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-21
Source: https://osv.dev/vulnerability/CVE-2026-55241
Type: osv

## Details
Checkmate is an open-source, self-hosted tool designed to track and monitor server hardware, uptime, response times, and incidents in real-time with beautiful visualizations. Prior to 3.9.1, the public POST /api/v1/auth/register route in server/src/api/routes/authRoutes.ts passes multipart profileImage uploads through in-memory Multer parsing before registration validation, without file-size, file-count, or MIME-type limits in server/src/api/middleware/upload.ts. An unauthenticated attacker can submit concurrent oversized files that are buffered before invalid registration or invite-token checks reject the request, exhausting memory and crashing or destabilizing the backend. This issue is fixed in version 3.9.1.

## References
- https://github.com/bluewave-labs/Checkmate/releases/tag/v3.9.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/55xxx/CVE-2026-55241.json
- https://github.com/bluewave-labs/Checkmate/security/advisories/GHSA-9xvg-x28f-m78m
- https://nvd.nist.gov/vuln/detail/CVE-2026-55241
- https://github.com/bluewave-labs/Checkmate/commit/091c36cbf338b673110b0806d76df26d52516468
