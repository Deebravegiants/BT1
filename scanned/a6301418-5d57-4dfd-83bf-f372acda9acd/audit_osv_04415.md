# [H] Unauthenticated access to new private chat messages in Discourse

## Summary
Severity: High
Advisory: BIT-discourse-2023-45131
Aliases: CVE-2023-45131, GHSA-84gf-hhrc-9pw6
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-discourse-2023-45131
Type: osv

## Affected
- Bitnami: `discourse` — affected unspecified

## Details
Discourse is an open source platform for community discussion. New chat messages can be read by making an unauthenticated POST request to MessageBus. This issue is patched in the 3.1.1 stable and 3.2.0.beta2 versions of Discourse. Users are advised to upgrade. There are no known workarounds for this vulnerability.

## References
- https://github.com/discourse/discourse/security/advisories/GHSA-84gf-hhrc-9pw6
- https://nvd.nist.gov/vuln/detail/CVE-2023-45131
