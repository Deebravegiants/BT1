# [M] Discourse's unscoped status lookups leak restricted metadata

## Summary
Severity: Medium
Advisory: BIT-discourse-2026-32114
Aliases: CVE-2026-32114, GHSA-3cvr-pm4c-hx96
Ecosystem: Bitnami
Published: 2026-03-27
Source: https://osv.dev/vulnerability/BIT-discourse-2026-32114
Type: osv

## Affected
- Bitnami: `discourse` — affected >=2026.3.0 <2026.3.0

## Details
Discourse is an open-source discussion platform. Prior to versions 2026.3.0, 2026.2.1, and 2026.1.2, there is an Insecure Direct Object Reference (IDOR) vulnerability that allows any authenticated user to access metadata about AI personas, features, and LLM models by providing their identifiers. This information includes credit allocations and usage statistics which are not intended to be public. The attack is performed over the network, requires low privileges (any logged-in user), and results in a low impact on confidentiality with no impact on integrity or availability. Versions 2026.3.0, 2026.2.1, and 2026.1.2 contain a patch. To work around this issue, disable AI plugin or upgrade to a patched version.

## References
- https://github.com/discourse/discourse/security/advisories/GHSA-3cvr-pm4c-hx96
- https://nvd.nist.gov/vuln/detail/CVE-2026-32114
