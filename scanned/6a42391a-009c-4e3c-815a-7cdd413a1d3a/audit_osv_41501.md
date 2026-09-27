# [H] Wallos: SSRF via OIDC Token/UserInfo URL Configuration

## Summary
Severity: High
Advisory: CVE-2026-61640
Aliases: GHSA-x9x5-gh69-q7cm
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-31
Source: https://osv.dev/vulnerability/CVE-2026-61640
Type: osv

## Details
Wallos is an open-source, self-hostable personal subscription tracker. Prior to version 4.9.6, Admin-configured OIDC token_url and user_info_url in includes/oidc/handle_oidc_callback.php:18-49 are used directly in curl_init() with zero SSRF filtering. Unlike logo/webhook URLs which have validate_webhook_url_for_ssrf(), OIDC URLs bypass all protections. Admin sets URL to http://169.254.169.254/latest/meta-data/ for cloud metadata access or internal network pivoting. This issue has been patched in version 4.9.6.

## References
- https://github.com/ellite/Wallos/releases/tag/v4.9.6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/61xxx/CVE-2026-61640.json
- https://github.com/ellite/Wallos/security/advisories/GHSA-x9x5-gh69-q7cm
- https://nvd.nist.gov/vuln/detail/CVE-2026-61640
- https://github.com/ellite/Wallos/commit/b75f13d0ffa3ed7e77e8e79e4b9fd3fc528c98d3
- https://github.com/ellite/Wallos/pull/1092
