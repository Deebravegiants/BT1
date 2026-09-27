# [M] Prevent unauthorized access to summary details in Discourse

## Summary
Severity: Medium
Advisory: BIT-discourse-2023-44391
Aliases: CVE-2023-44391, GHSA-7px5-fqcf-7mfr
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-discourse-2023-44391
Type: osv

## Affected
- Bitnami: `discourse` — affected unspecified

## Details
Discourse is an open source platform for community discussion. User summaries are accessible for anonymous users even when `hide_user_profiles_from_public` is enabled. This problem has been patched in the 3.1.1 stable and 3.2.0.beta2 version of Discourse. Users are advised to upgrade. There are no known workarounds for this vulnerability.

## References
- https://github.com/discourse/discourse/security/advisories/GHSA-7px5-fqcf-7mfr
- https://nvd.nist.gov/vuln/detail/CVE-2023-44391
