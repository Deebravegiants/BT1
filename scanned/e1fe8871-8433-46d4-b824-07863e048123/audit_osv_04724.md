# [H] Incorrect Authorization in Kibana Agent Builder Leading to Disclosure and Tampering of Private Agents

## Summary
Severity: High
Advisory: BIT-elk-2026-72643
Aliases: BIT-kibana-2026-72643, CVE-2026-72643
Ecosystem: Bitnami
Published: 2026-08-19
Source: https://osv.dev/vulnerability/BIT-elk-2026-72643
Type: osv

## Affected
- Bitnami: `elk` — affected >=9.5.0 <9.5.1

## Details
Kibana Agent Builder determines whether a caller owns a private agent by comparing a stable user identifier when one is recorded, and falling back to a comparison of the username when it is not. A username is not unique across Elasticsearch authentication realms, so two distinct principals that share a username in different realms are treated as the same owner. This discloses the configuration and instructions of an agent the caller does not own, and allows that agent to be altered or removed.

## References
- https://discuss.elastic.co/t/kibana-9-4-5-9-5-1-security-update-esa-2026-124/389538
- https://nvd.nist.gov/vuln/detail/CVE-2026-72643
