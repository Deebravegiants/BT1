# [M] WACRM: SSRF via the automation `send_webhook` action

## Summary
Severity: Medium
Advisory: CVE-2026-67530
Aliases: GHSA-8jqh-598v-rfxc
CVSS: 6.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:L/A:N)
Published: 2026-07-30
Source: https://osv.dev/vulnerability/CVE-2026-67530
Type: osv

## Details
WACRM is a self-hostable CRM template for WhatsApp. In 0.7.0 and earlier, the automation send_webhook action in src/lib/automations/engine.ts and its validation in src/lib/automations/validate.ts allowed an authenticated user with automation privileges to submit an arbitrary webhook URL that the server fetched without the existing isDeliverableUrl SSRF guard in src/lib/webhooks/ssrf.ts, allowing requests to private, loopback, link-local, or cloud metadata addresses such as the cloud metadata endpoint at 169.254.169.254. This vulnerability is fixed with commit 23838a9959550e975d732ae08a44a3a2f0cc084b.

## References
- https://github.com/ArnasDon/wacrm/security/advisories/GHSA-8jqh-598v-rfxc
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/67xxx/CVE-2026-67530.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-67530
- https://github.com/ArnasDon/wacrm/commit/23838a9959550e975d732ae08a44a3a2f0cc084b
