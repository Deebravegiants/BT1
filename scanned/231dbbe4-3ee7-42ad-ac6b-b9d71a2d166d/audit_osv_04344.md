# [M] Anonymous user cache poisoning via development-mode header in Discourse

## Summary
Severity: Medium
Advisory: BIT-discourse-2021-43794
Aliases: CVE-2021-43794, GHSA-249g-pc77-65hp
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-discourse-2021-43794
Type: osv

## Affected
- Bitnami: `discourse` — affected >=0 <2.7.11

## Details
Discourse is an open source discussion platform. In affected versions an attacker can poison the cache for anonymous (i.e. not logged in) users, such that the users are shown a JSON blob instead of the HTML page. This can lead to a partial denial-of-service. This issue is patched in the latest stable, beta and tests-passed versions of Discourse.

## References
- https://github.com/discourse/discourse/commit/2da0001965c6d8632d723c46ea5df9f22a1a23f1
- https://github.com/discourse/discourse/security/advisories/GHSA-249g-pc77-65hp
- https://nvd.nist.gov/vuln/detail/CVE-2021-43794
