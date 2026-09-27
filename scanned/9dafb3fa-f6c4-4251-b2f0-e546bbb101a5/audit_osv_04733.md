# [M] Authorization Bypass Through User-Controlled Key in Kibana Agent Builder Leading to Unauthorized Data Modification

## Summary
Severity: Medium
Advisory: BIT-elk-2026-72680
Aliases: BIT-kibana-2026-72680, CVE-2026-72680
Ecosystem: Bitnami
Published: 2026-08-19
Source: https://osv.dev/vulnerability/BIT-elk-2026-72680
Type: osv

## Affected
- Bitnami: `elk` — affected >=9.2.0 <9.4.5

## Details
Kibana Agent Builder A2A JSON-RPC API endpoint derives the identifier of a stored conversation from a user-supplied input, and the ownership check on that identifier does not distinguish between a conversation that does not exist and one that exists but belongs to another user. As a result, an authenticated user holding only the Agent Builder read privilege can supply an identifier already in use by another user in the same space and cause that user's conversation to be replaced and reassigned to the requesting account. The original owner permanently loses access to the conversation and its history. The impact is limited to loss of integrity and availability of the affected conversation; the attacker does not read the overwritten content.

## References
- https://discuss.elastic.co/t/kibana-9-4-5-security-update-esa-2026-82/389535
- https://nvd.nist.gov/vuln/detail/CVE-2026-72680
