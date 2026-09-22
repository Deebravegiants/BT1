# [M] Incomplete List of Disallowed Inputs in Kibana Leading to Server-Side Request Forgery

## Summary
Severity: Medium
Advisory: BIT-kibana-2026-63142
Aliases: BIT-elk-2026-63142, CVE-2026-63142
Ecosystem: Bitnami
Published: 2026-07-28
Source: https://osv.dev/vulnerability/BIT-kibana-2026-63142
Type: osv

## Affected
- Bitnami: `kibana` — affected >=9.4.0 <9.4.4

## Details
Incomplete List of Disallowed Inputs (CWE-184) in Kibana can allow an authenticated attacker with access to the Reporting feature to bypass outbound request restrictions configured by an administrator, causing the reporting service to send requests to network destinations that should be denied by the configured security policy.

## References
- https://discuss.elastic.co/t/kibana-8-19-19-9-3-8-9-4-4-security-update-esa-2026-66/388568
- https://nvd.nist.gov/vuln/detail/CVE-2026-63142
