# [H] Incorrect Authorization in Kibana Fleet Leading to Privilege Escalation

## Summary
Severity: High
Advisory: BIT-elk-2026-72630
Aliases: BIT-kibana-2026-72630, CVE-2026-72630
Ecosystem: Bitnami
Published: 2026-08-19
Source: https://osv.dev/vulnerability/BIT-elk-2026-72630
Type: osv

## Affected
- Bitnami: `elk` — affected >=9.5.0 <9.5.1

## Details
Incorrect Authorization (CWE-863) in Kibana Fleet can lead to privilege escalation via Privilege Abuse (CAPEC-122). Fleet restricts some callers to managing integration policies for one specific integration. When an existing integration policy was updated, that restriction was evaluated against the integration recorded on the stored policy rather than against the replacement integration supplied with the update. An authenticated user holding only the Elastic Defend endpoint policy management privilege was therefore able to convert an endpoint policy they administer into a policy for a different integration, and to supply that integration's configuration at the same time.

## References
- https://discuss.elastic.co/t/kibana-8-19-20-9-4-5-9-5-1-security-update-esa-2026-127/389531
- https://nvd.nist.gov/vuln/detail/CVE-2026-72630
