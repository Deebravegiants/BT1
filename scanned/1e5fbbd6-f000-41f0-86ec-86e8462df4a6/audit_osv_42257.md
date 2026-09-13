# [H] Frappe: Improper Authorization in OAuth2 Consent Endpoint

## Summary
Severity: High
Advisory: CVE-2026-66001
Aliases: GHSA-2ph8-x773-8p2x
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:A/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-20
Source: https://osv.dev/vulnerability/CVE-2026-66001
Type: osv

## Details
Frappe is a full-stack web application framework. Prior to 15.114.0 and 16.26.0, the approve and authorize functions in frappe/integrations/oauth2.py allow the OAuth2 consent flow to proceed without restricting approve to POST, without a csrf_token in frappe/templates/includes/oauth_confirmation.html, and without scoping an active OAuth token check to the requesting client. An attacker can cause an authenticated user to approve an OAuth grant or reuse authorization state for the wrong client, exposing data and permitting actions within the granted scopes. This issue is fixed in versions 15.114.0 and 16.26.0.

## References
- https://github.com/frappe/frappe/releases/tag/v15.114.0
- https://github.com/frappe/frappe/releases/tag/v16.26.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/66xxx/CVE-2026-66001.json
- https://github.com/frappe/frappe/security/advisories/GHSA-2ph8-x773-8p2x
- https://nvd.nist.gov/vuln/detail/CVE-2026-66001
- https://github.com/frappe/frappe/commit/336c7d335db762b494acdfe43aea69d459fd51d7
- https://github.com/frappe/frappe/commit/d7460769f999c68d3121b680119f8724ddd3eb9d
- https://github.com/frappe/frappe/commit/eb9c1446cac13236c6d573b136786db2e46254fa
- https://github.com/frappe/frappe/pull/40073
- https://github.com/frappe/frappe/pull/40700
- https://github.com/frappe/frappe/pull/40701
