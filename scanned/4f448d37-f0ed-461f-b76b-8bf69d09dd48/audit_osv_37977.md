# [H] cronmaster: Middleware authentication bypass enabling unauthorized page access and server-action execution

## Summary
Severity: High
Advisory: CVE-2026-34072
Aliases: GHSA-9whh-mffv-xvh6
CVSS: 8.3 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:L)
Published: 2026-04-01
Source: https://osv.dev/vulnerability/CVE-2026-34072
Type: osv

## Details
Cr*nMaster (cronmaster) is a Cronjob management UI with human readable syntax, live logging and log history for cronjobs. Prior to version 2.2.0, an authentication bypass in middleware allows unauthenticated requests with an invalid session cookie to be treated as authenticated when the middleware’s session-validation fetch fails. This can result in unauthorized access to protected pages and unauthorized execution of privileged Next.js Server Actions. This issue has been patched in version 2.2.0.

## References
- https://github.com/fccview/cronmaster/releases/tag/2.2.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34072.json
- https://github.com/fccview/cronmaster/security/advisories/GHSA-9whh-mffv-xvh6
- https://nvd.nist.gov/vuln/detail/CVE-2026-34072
