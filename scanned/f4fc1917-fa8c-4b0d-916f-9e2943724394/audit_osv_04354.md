# [M] Secure category names leaked via user activity export in Discourse

## Summary
Severity: Medium
Advisory: BIT-discourse-2022-24782
Aliases: CVE-2022-24782, GHSA-c3cq-w899-f343
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-discourse-2022-24782
Type: osv

## Affected
- Bitnami: `discourse` — affected >=0 <2.8.3

## Details
Discourse is an open source discussion platform. Versions 2.8.2 and prior in the `stable` branch, 2.9.0.beta3 and prior in the `beta` branch, and 2.9.0.beta3 and prior in the `tests-passed` branch are vulnerable to a data leak. Users can request an export of their own activity. Sometimes, due to category settings, they may have category membership for a secure category. The name of this secure category is shown to the user in the export. The same thing occurs when the user's post has been moved to a secure category. A patch for this issue is available in the `main` branch of Discourse's GitHub repository and is anticipated to be part of future releases.

## References
- https://github.com/discourse/discourse/commit/9d5737fd28374cc876c070f6c3a931a8071ec356
- https://github.com/discourse/discourse/pull/16273
- https://github.com/discourse/discourse/security/advisories/GHSA-c3cq-w899-f343
- https://nvd.nist.gov/vuln/detail/CVE-2022-24782
