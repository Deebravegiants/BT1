# [H] FUXA: JWT lifecycle flaws allow deleted or demoted users to retain privileged sessions

## Summary
Severity: High
Advisory: CVE-2026-65984
Aliases: GHSA-rg7m-xwqc-mjw6
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:P/PR:H/UI:N/VC:H/VI:H/VA:L/SC:N/SI:N/SA:N)
Published: 2026-08-18
Source: https://osv.dev/vulnerability/CVE-2026-65984
Type: osv

## Details
FUXA is a web-based Process Visualization (SCADA/HMI/Dashboard) software. In 1.3.2 and earlier, POST /api/refresh in server/api/auth/index.js falls back from current user data to decoded.groups, including when the user is deleted or groups is zero, and POST /api/heartbeat in server/api/index.js re-signs inbound JWT claims without validating the current database record. An attacker who possesses a previously issued privileged refresh cookie or access token can continue minting privileged JWTs after account deletion, disablement, role removal, or demotion. Continued refresh-cookie rotation can extend the stale session and preserve unauthorized access to user management, project manipulation, runtime configuration, scripts, and backdoor-account creation. This issue is fixed in version 1.3.3.

## References
- https://github.com/frangoteam/FUXA/releases/tag/v1.3.3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/65xxx/CVE-2026-65984.json
- https://github.com/frangoteam/FUXA/security/advisories/GHSA-rg7m-xwqc-mjw6
- https://nvd.nist.gov/vuln/detail/CVE-2026-65984
- https://github.com/frangoteam/FUXA/commit/4fa47d0a2a856ed34f427f472fb4450f86e7749b
- https://github.com/frangoteam/FUXA/pull/2379
