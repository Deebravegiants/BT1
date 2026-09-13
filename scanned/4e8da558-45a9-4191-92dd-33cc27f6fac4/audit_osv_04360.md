# [H] Email activation route can be abused by spammers in Discourse

## Summary
Severity: High
Advisory: BIT-discourse-2022-31184
Aliases: CVE-2022-31184, GHSA-m5w9-8gp8-2hrf
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-discourse-2022-31184
Type: osv

## Affected
- Bitnami: `discourse` — affected unspecified

## Details
Discourse is the an open source discussion platform. In affected versions an email activation route can be abused to send mass spam emails. A fix has been included in the latest stable, beta and tests-passed versions of Discourse which rate limits emails. Users are advised to upgrade. Users unable to upgrade should manually rate limit email.

## References
- https://github.com/discourse/discourse/commit/af1cb735db7fb73217b85d22dbadd1bc824ac0b0
- https://github.com/discourse/discourse/security/advisories/GHSA-m5w9-8gp8-2hrf
- https://nvd.nist.gov/vuln/detail/CVE-2022-31184
