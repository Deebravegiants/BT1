# [M] Incorrect Authorization in Kibana Fleet Leading to Information Disclosure

## Summary
Severity: Medium
Advisory: BIT-elk-2026-33460
Aliases: BIT-kibana-2026-33460, CVE-2026-33460
Ecosystem: Bitnami
Published: 2026-04-13
Source: https://osv.dev/vulnerability/BIT-elk-2026-33460
Type: osv

## Affected
- Bitnami: `elk` — affected >=9.3.0 <9.3.3

## Details
Incorrect Authorization (CWE-863) in Kibana can lead to cross-space information disclosure via Privilege Abuse (CAPEC-122). A user with Fleet agent management privileges in one Kibana space can retrieve Fleet Server policy details from other spaces through an internal enrollment endpoint. The endpoint bypasses space-scoped access controls by using an unscoped internal client, returning operational identifiers, policy names, management state, and infrastructure linkage details from spaces the user is not authorized to access.

## References
- https://discuss.elastic.co/t/kibana-8-19-14-9-2-8-9-3-3-security-update-esa-2026-25/385813
- https://nvd.nist.gov/vuln/detail/CVE-2026-33460
