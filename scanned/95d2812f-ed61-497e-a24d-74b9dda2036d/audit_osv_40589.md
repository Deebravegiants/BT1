# [C] FOSSBilling: Client password reset token reuse allows persistent account takeover

## Summary
Severity: Critical
Advisory: CVE-2026-53646
Aliases: GHSA-vp66-w6rc-x32p
CVSS: 9.0 (CVSS:4.0/AV:N/AC:H/AT:P/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-06
Source: https://osv.dev/vulnerability/CVE-2026-53646
Type: osv

## Details
FOSSBilling is a free, open-source billing and client management system. In versions 0.5.6 through 0.7.2, when a `ClientPasswordReset` record already exists for a client (from a previous unexpired reset request), subsequent calls to the `reset_password` guest API endpoint reuse the existing token instead of generating a new one. The 15-minute validity window is anchored to the first request's `created_at` timestamp, not the time of the most recent email. An attacker who obtained the original reset link remains able to use it even after the victim requests a new reset, because the original token is never invalidated or rotated. Version 0.8.0 patches the issue. Some workarounds are available. Configure a reverse proxy (e.g., Nginx, Apache, Cloudflare) to apply per-IP rate limiting to the `/client/reset-password` endpoint to minimize the window of opportunity, and/or manually clear expired `client_password_reset` records from the database after a client reports a suspected compromise.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53646.json
- https://github.com/FOSSBilling/FOSSBilling/security/advisories/GHSA-vp66-w6rc-x32p
- https://nvd.nist.gov/vuln/detail/CVE-2026-53646
