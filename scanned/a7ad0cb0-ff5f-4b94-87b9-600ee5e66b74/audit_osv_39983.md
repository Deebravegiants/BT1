# [C] Postiz has cross-tenant SUPERADMIN takeover via Skool-provider JWT forgery

## Summary
Severity: Critical
Advisory: CVE-2026-48781
Aliases: GHSA-j77w-h625-56q2
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-06-16
Source: https://osv.dev/vulnerability/CVE-2026-48781
Type: osv

## Details
Postiz is an AI social media scheduling tool. In versions prior to 2.21.8, the Skool integration callback signed an attacker-controlled JSON blob into a session-shape JWT using the application's JWT_SECRET, and the auth middleware trusted every claim in that JWT without re-resolving the user from the database. Any authenticated Postiz user could forge a SUPERADMIN session and impersonate arbitrary organizations. This allowed Full Access to the following: all parts of Postiz, including users registered to the specific instance and the ability to post in the name of the victim's social media channels added to that Postiz instance. This issue has been fixed in version 2.21.8.

## References
- http://github.com/gitroomhq/postiz-app/releases/tag/v2.21.8
- https://gadvisory.org/advisories/PSA-2026-2CAQ96
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/48xxx/CVE-2026-48781.json
- https://github.com/gitroomhq/postiz-app/security/advisories/GHSA-j77w-h625-56q2
- https://nvd.nist.gov/vuln/detail/CVE-2026-48781
- https://github.com/gitroomhq/postiz-app/commit/23696d2973510ae1f3f48bfa41a6bfbbf9827b05
