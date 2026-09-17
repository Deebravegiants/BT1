# [C] Grav before 1.0.4 Password Reset Token Poisoning via admin_base_url

## Summary
Severity: Critical
Advisory: CVE-2026-61451
Aliases: GHSA-5xc4-j99p-cp4m
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2026-07-15
Source: https://osv.dev/vulnerability/CVE-2026-61451
Type: osv

## Details
The Grav API plugin (grav-plugin-api) before 1.0.4 does not validate the origin of the client-supplied admin_base_url field in the POST /api/v1/auth/forgot-password endpoint. The sanitizeHttpUrl() function only checks that the URL scheme is http/https and never verifies the host against the server's own origin, so an attacker can supply an arbitrary host. As a result, an unauthenticated attacker can cause the password reset email sent to a victim to contain a reset link pointing at an attacker-controlled server; when the victim follows the link, the valid reset token is disclosed to the attacker, enabling full account takeover. The vulnerable base URL can also be influenced via the Referer or Origin headers.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/61xxx/CVE-2026-61451.json
- https://github.com/getgrav/grav/security/advisories/GHSA-5xc4-j99p-cp4m
- https://nvd.nist.gov/vuln/detail/CVE-2026-61451
- https://www.vulncheck.com/advisories/grav-before-password-reset-token-poisoning-via-admin-base-url
