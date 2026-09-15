# [M] Vexa Webhook Feature has a SSRF Vulnerability

## Summary
Severity: Medium
Advisory: CVE-2026-25883
Aliases: GHSA-fhr6-8hff-cvg4
CVSS: 5.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:N/A:N)
Published: 2026-04-20
Source: https://osv.dev/vulnerability/CVE-2026-25883
Type: osv

## Details
Vexa is an open-source, self-hostable meeting bot API and meeting transcription API. Prior to 0.10.0-260419-1910, the Vexa webhook feature allows authenticated users to configure an arbitrary URL that receives HTTP POST requests when meetings complete. The application performs no validation on the webhook URL, enabling Server-Side Request Forgery (SSRF). An authenticated attacker can set their webhook URL to target internal services (Redis, databases, admin panels), cloud metadata endpoints (AWS/GCP credential theft), and/or localhost services. Version 0.10.0-260419-1910 patches the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/25xxx/CVE-2026-25883.json
- https://github.com/Vexa-ai/vexa/security/advisories/GHSA-fhr6-8hff-cvg4
- https://nvd.nist.gov/vuln/detail/CVE-2026-25883
