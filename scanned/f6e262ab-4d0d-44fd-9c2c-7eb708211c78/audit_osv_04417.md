# [M] Discourse vulnerable to DoS via Regexp Injection in Full Name

## Summary
Severity: Medium
Advisory: BIT-discourse-2023-45806
Aliases: CVE-2023-45806, GHSA-hcgf-hg2g-mw78
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-discourse-2023-45806
Type: osv

## Affected
- Bitnami: `discourse` — affected >=0 <3.2.0

## Details
Discourse is an open source platform for community discussion. Prior to version 3.1.3 of the `stable` branch and version 3.2.0.beta3 of the `beta` and `tests-passed` branches, if a user has been quoted and uses a `|` in their full name, they might be able to trigger a bug that generates a lot of duplicate content in all the posts they've been quoted by updating their full name again. Version 3.1.3 of the `stable` branch and version 3.2.0.beta3 of the `beta` and `tests-passed` branches contain a patch for this issue. No known workaround exists, although one can stop the "bleeding" by ensuring users only use alphanumeric characters in their full name field.

## References
- https://github.com/discourse/discourse/commit/2ec25105179199cf80912bf011c18b8b870e1863
- https://github.com/discourse/discourse/commit/7d484864fe91ff79c478f57e7ddb1235d701921e
- https://github.com/discourse/discourse/security/advisories/GHSA-hcgf-hg2g-mw78
- https://nvd.nist.gov/vuln/detail/CVE-2023-45806
