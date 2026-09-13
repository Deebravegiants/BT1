# [M] Dradis Community Edition 5.1.0 through 5.2.0 Server-Side Request Forgery via Unrestricted AI Provider Address

## Summary
Severity: Medium
Advisory: CVE-2026-79788
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:L/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-25
Source: https://osv.dev/vulnerability/CVE-2026-79788
Type: osv

## Details
In Dradis Community Edition, the ProvidersController and AgentsController gate their admin_required before_action on `defined?(Dradis::Pro)`, a constant that is never defined in CE, so the authorization check is never applied. As a result, any authenticated (non-admin) user can create an AI provider pointing to an arbitrary HTTP/HTTPS address (including internal/link-local hosts such as http://169.254.169.254) and reassign the built-in Roslin agent to use it. When an AI interaction is triggered, the server issues a request to the attacker-supplied URL (server-side request forgery). For non-2xx responses, the target's response body is reflected verbatim to the attacker's browser via ActionCable/Turbo Stream error messages, making the SSRF readable.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/79xxx/CVE-2026-79788.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-79788
- https://www.vulncheck.com/advisories/dradis-community-edition-5.1.0-through-5.2.0-server-side-request-forgery-via-unrestricted-ai-provider-address
- https://github.com/dradis/dradis-ce/issues/1641
- https://github.com/dradis/dradis-ce
- https://github.com/dradis/dradis-ce/blob/v5.2.0/engines/dradis-echo/app/controllers/dradis/plugins/echo/providers_controller.rb
