# [M] Discourse vulnerable to DoS via defer queue

## Summary
Severity: Medium
Advisory: BIT-discourse-2023-38498
Aliases: CVE-2023-38498, GHSA-wv29-rm3f-4g2j
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-discourse-2023-38498
Type: osv

## Affected
- Bitnami: `discourse` — affected >=0 <3.0.6

## Details
Discourse is an open source discussion platform. Prior to version 3.0.6 of the `stable` branch and version 3.1.0.beta7 of the `beta` and `tests-passed` branches, a malicious user can prevent the defer queue from proceeding promptly on sites hosted in the same multisite installation. The issue is patched in version 3.0.6 of the `stable` branch and version 3.1.0.beta7 of the `beta` and `tests-passed` branches. There are no known workarounds for this vulnerability. Users of multisite configurations should upgrade.

## References
- https://github.com/discourse/discourse/commit/26e267478d785e2f32ee7da4613e2cf4a65ff182
- https://github.com/discourse/discourse/security/advisories/GHSA-wv29-rm3f-4g2j
- https://nvd.nist.gov/vuln/detail/CVE-2023-38498
