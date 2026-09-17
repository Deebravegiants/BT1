# [H] Taultulli has CSRF in /configUpdate via missing anti-CSRF and method restriction that allows admin credential takeover

## Summary
Severity: High
Advisory: CVE-2026-43985
Aliases: GHSA-v622-pmjj-gpx3
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-06-04
Source: https://osv.dev/vulnerability/CVE-2026-43985
Type: osv

## Details
Tautulli is a Python based monitoring and tracking tool for Plex Media Server. Versions prior to 2.17.1 expose `configUpdate` as a state-changing administrator endpoint, but the route does not enforce `POST` and does not use any anti-CSRF token. In the default form and JWT-based authentication mode, the administrator session cookie is issued with `SameSite=Lax`, which still permits top-level cross-site navigation requests. An attacker can exploit this by luring a logged-in administrator to a malicious page that submits a cross-site request to `/configUpdate` and overwrites the local administrator username and password. The attacker can then sign in directly with the chosen credentials and take over the Tautulli administrative interface. Version 2.17.1 patches the issue.

## References
- https://github.com/Tautulli/Tautulli/releases/tag/v2.17.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43985.json
- https://github.com/Tautulli/Tautulli/security/advisories/GHSA-v622-pmjj-gpx3
- https://nvd.nist.gov/vuln/detail/CVE-2026-43985
