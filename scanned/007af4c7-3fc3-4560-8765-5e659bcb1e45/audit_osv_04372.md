# [M] Discourse may allow exposure of hidden tags in the subject of notification emails

## Summary
Severity: Medium
Advisory: BIT-discourse-2022-46150
Aliases: CVE-2022-46150, GHSA-rqvq-94h8-p5wv
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-discourse-2022-46150
Type: osv

## Affected
- Bitnami: `discourse` — affected >=0 <2.8.13

## Details
Discourse is an open-source discussion platform. Prior to version 2.8.13 of the `stable` branch and version 2.9.0.beta14 of the `beta` and `tests-passed` branches, unauthorized users may learn of the existence of hidden tags and that they have been applied to topics that they have access to. This issue is patched in version 2.8.13 of the `stable` branch and version 2.9.0.beta14 of the `beta` and `tests-passed` branches. As a workaround, use the `disable_email` site setting to disable all emails to non-staff users.

## References
- https://github.com/discourse/discourse/commit/84c83e8d4a1907f8a2972f0ab44b6402aa910c3b
- https://github.com/discourse/discourse/security/advisories/GHSA-rqvq-94h8-p5wv
- https://nvd.nist.gov/vuln/detail/CVE-2022-46150
