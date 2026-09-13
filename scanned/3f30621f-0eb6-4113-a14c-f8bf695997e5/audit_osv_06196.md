# [H] Missing Authorization in Kibana Leading to Cross-User Information Disclosure and Data Tampering

## Summary
Severity: High
Advisory: BIT-kibana-2026-72669
Aliases: BIT-elk-2026-72669, CVE-2026-72669
Ecosystem: Bitnami
Published: 2026-08-19
Source: https://osv.dev/vulnerability/BIT-kibana-2026-72669
Type: osv

## Affected
- Bitnami: `kibana` — affected >=9.0.0 <9.4.5

## Details
The state that Kibana stores for an Observability Onboarding flow is not bound to the user who created the flow, and the routes that read and update that state do not verify ownership. An authenticated user who holds only generic read access to the space can therefore discover the onboarding flows of other users, read their onboarding state, and write arbitrary progress data into them. A tampered flow can also cause the owner's onboarding view to fail with a server error.

## References
- https://discuss.elastic.co/t/kibana-8-19-19-and-9-4-5-security-update-esa-2026-86/389515
- https://nvd.nist.gov/vuln/detail/CVE-2026-72669
