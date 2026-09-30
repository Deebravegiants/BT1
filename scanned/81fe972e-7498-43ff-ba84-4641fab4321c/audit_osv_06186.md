# [H] External Control of File Name or Path and Server-Side Request Forgery (SSRF) in Kibana Google Gemini Connector

## Summary
Severity: High
Advisory: BIT-kibana-2026-0532
Aliases: BIT-elk-2026-0532, CVE-2026-0532
Ecosystem: Bitnami
Published: 2026-01-16
Source: https://osv.dev/vulnerability/BIT-kibana-2026-0532
Type: osv

## Affected
- Bitnami: `kibana` — affected >=9.2.0 <9.2.4

## Details
External Control of File Name or Path (CWE-73) combined with Server-Side Request Forgery (CWE-918) can allow an attacker to cause arbitrary file disclosure through a specially crafted credentials JSON payload in the Google Gemini connector configuration. This requires an attacker to have authenticated access with privileges sufficient to create or modify connectors (Alerts & Connectors: All). The server processes a configuration without proper validation, allowing for arbitrary network requests and for arbitrary file reads.

## References
- https://discuss.elastic.co/t/kibana-8-19-10-9-1-10-9-2-4-security-update-esa-2026-05/384524
- https://nvd.nist.gov/vuln/detail/CVE-2026-0532
- https://access.redhat.com/security/cve/CVE-2026-0532
- https://bugzilla.redhat.com/show_bug.cgi?id=2429540
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-0532.json
