# [H] Discourse vulnerable to DoS via large URL payload in PM to a bot

## Summary
Severity: High
Advisory: BIT-discourse-2025-48053
Aliases: CVE-2025-48053, GHSA-3q5q-qmrm-rvwx
Ecosystem: Bitnami
Published: 2025-06-11
Source: https://osv.dev/vulnerability/BIT-discourse-2025-48053
Type: osv

## Affected
- Bitnami: `discourse` — affected >=0 <3.4.4

## Details
Discourse is an open-source discussion platform. Prior to version 3.4.4 of the `stable` branch, version 3.5.0.beta5 of the `beta` branch, and version 3.5.0.beta6-dev of the `tests-passed` branch, sending a malicious URL in a PM to a bot user can cause a reduced the availability of a Discourse instance. This issue is patched in version 3.4.4 of the `stable` branch, version 3.5.0.beta5 of the `beta` branch, and version 3.5.0.beta6-dev of the `tests-passed` branch. No known workarounds are available.

## References
- https://github.com/discourse/discourse/security/advisories/GHSA-3q5q-qmrm-rvwx
- https://nvd.nist.gov/vuln/detail/CVE-2025-48053
