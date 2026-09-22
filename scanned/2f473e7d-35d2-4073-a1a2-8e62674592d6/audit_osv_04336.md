# [H] Re-use of email tokens in Discourse

## Summary
Severity: High
Advisory: BIT-discourse-2021-37693
Aliases: CVE-2021-37693, GHSA-9377-96f4-cww4
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-discourse-2021-37693
Type: osv

## Affected
- Bitnami: `discourse` — affected >=0 <2.7.8

## Details
Discourse is an open-source platform for community discussion. In Discourse before versions 2.7.8 and 2.8.0.beta4, when adding additional email addresses to an existing account on a Discourse site an email token is generated as part of the email verification process. Deleting the additional email address does not invalidate an unused token which can then be used in other contexts, including reseting a password.

## References
- https://github.com/discourse/discourse/commit/fb14e50741a4880cda22244eded8858e2f5336ef
- https://github.com/discourse/discourse/security/advisories/GHSA-9377-96f4-cww4
- https://nvd.nist.gov/vuln/detail/CVE-2021-37693
