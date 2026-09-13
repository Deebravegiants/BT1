# [C] Squidex has Server-Side Request Forgery (SSRF) Issue in Webhook Configuration

## Summary
Severity: Critical
Advisory: CVE-2026-24736
Aliases: GHSA-wxg2-953m-fg2w
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-01-27
Source: https://osv.dev/vulnerability/CVE-2026-24736
Type: osv

## Details
Squidex is an open source headless content management system and content management hub. Versions of the application up to and including 7.21.0 allow users to define "Webhooks" as actions within the Rules engine. The url parameter in the webhook configuration does not appear to validate or restrict destination IP addresses. It accepts local addresses such as 127.0.0.1 or localhost. When a rule is triggered (Either manual trigger by manually calling the trigger endpoint or by a content update or any other triggers), the backend server executes an HTTP request to the user-supplied URL. Crucially, the server logs the full HTTP response in the rule execution log (lastDump field), which is accessible via the API. Which turns a "Blind" SSRF into a "Full Read" SSRF. As of time of publication, no patched versions are available.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/24xxx/CVE-2026-24736.json
- https://github.com/Squidex/squidex/security/advisories/GHSA-wxg2-953m-fg2w
- https://nvd.nist.gov/vuln/detail/CVE-2026-24736
