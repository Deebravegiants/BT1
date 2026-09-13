# [H] Wallos: SSRF Bypass - Incomplete Fix for CVE-2026-30839/30840

## Summary
Severity: High
Advisory: CVE-2026-33399
Aliases: GHSA-mfjc-3258-cq3j
CVSS: 7.7 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N)
Published: 2026-03-24
Source: https://osv.dev/vulnerability/CVE-2026-33399
Type: osv

## Details
Wallos is an open-source, self-hostable personal subscription tracker. Prior to version 4.7.0, the SSRF fix applied in version 4.6.2 for CVE-2026-30839 and CVE-2026-30840 is incomplete. The validate_webhook_url_for_ssrf() protection was added to the test* notification endpoints but not to the corresponding save* endpoints. An authenticated user can save an internal/private IP address as a notification URL, and when the cron job sendnotifications.php executes, the request is sent to the internal IP without any SSRF validation. This issue has been patched in version 4.7.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33399.json
- https://github.com/ellite/Wallos/security/advisories/GHSA-mfjc-3258-cq3j
- https://nvd.nist.gov/vuln/detail/CVE-2026-33399
- https://github.com/ellite/Wallos/commit/e87387f0ebb540cd33e6dfda7181db9db650ecef#diff-d77202c5d47a3d7d4586e519f6f5e256da5fb2969fa8b9c75c399b2821e9de40
