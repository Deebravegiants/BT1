# [M] PraisonAI before 4.6.78 Missing Webhook Signature Verification

## Summary
Severity: Medium
Advisory: CVE-2026-61436
Aliases: GHSA-7c92-x8vg-4258
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:H/VA:L/SC:N/SI:N/SA:N)
Published: 2026-07-15
Source: https://osv.dev/vulnerability/CVE-2026-61436
Type: osv

## Details
PraisonAI before 4.6.78 fails to verify Svix webhook signatures in AgentMail webhook mode, allowing unauthenticated attackers to forge message.received events. Attackers can send crafted JSON payloads to the webhook endpoint to invoke configured agents with arbitrary sender addresses and message content.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/61xxx/CVE-2026-61436.json
- https://github.com/MervinPraison/PraisonAI/security/advisories/GHSA-7c92-x8vg-4258
- https://nvd.nist.gov/vuln/detail/CVE-2026-61436
- https://www.vulncheck.com/advisories/praisonai-before-missing-webhook-signature-verification
- https://github.com/MervinPraison/PraisonAI/commit/2a855c470077c7d2e2479a575f7ef7f548d51c33
- https://github.com/MervinPraison/PraisonAI/commit/846568c7a5d8ce9e71e56e4c213f027c04909753
