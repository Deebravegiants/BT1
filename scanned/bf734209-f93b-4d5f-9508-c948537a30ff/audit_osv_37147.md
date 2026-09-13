# [H] dsa-hub-server: Clear-Text Storage of Sensitive Data

## Summary
Severity: High
Advisory: CVE-2026-28678
Aliases: GHSA-vmxr-562h-rcgg
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:N)
Published: 2026-03-07
Source: https://osv.dev/vulnerability/CVE-2026-28678
Type: osv

## Details
DSA Study Hub is an interactive educational web application. Prior to commit d527fba, the user authentication system in server/routes/auth.js was found to be vulnerable to Insufficiently Protected Credentials. Authentication tokens (JWTs) were stored in HTTP cookies without cryptographic protection of the payload. This issue has been patched via commit d527fba.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/28xxx/CVE-2026-28678.json
- https://github.com/toxicbishop/DSA-with-tsx/security/advisories/GHSA-vmxr-562h-rcgg
- https://nvd.nist.gov/vuln/detail/CVE-2026-28678
- https://github.com/toxicbishop/DSA-with-tsx/commit/d527fba3b3c15f185b9d1e730322dff9248391e4
