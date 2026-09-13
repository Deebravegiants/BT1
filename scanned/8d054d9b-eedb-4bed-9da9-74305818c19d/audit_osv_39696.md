# [M] e107: CSRF in comment.php moderation endpoints via token-optional validation in session_handler::check()

## Summary
Severity: Medium
Advisory: CVE-2026-46620
Aliases: GHSA-m4hh-m278-jwg5
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N)
Published: 2026-05-26
Source: https://osv.dev/vulnerability/CVE-2026-46620
Type: osv

## Details
e107 is a content management system (CMS). Prior to 2.3.5, e107 CMS does not properly enforce CSRF token validation on comment moderation actions. The problem comes down to how session_handler::check() handles CSRF tokens. Instead of requiring a token on every state-changing request, it only validates the token if one happens to be present. If there is no token at all, the check is skipped entirely. This vulnerability is fixed in 2.3.5.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46620.json
- https://github.com/e107inc/e107/security/advisories/GHSA-m4hh-m278-jwg5
- https://nvd.nist.gov/vuln/detail/CVE-2026-46620
