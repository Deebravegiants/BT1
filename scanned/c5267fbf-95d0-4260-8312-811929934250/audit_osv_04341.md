# [M] Cache poisoning via maliciously-formed request in discourse

## Summary
Severity: Medium
Advisory: BIT-discourse-2021-41271
Aliases: CVE-2021-41271, GHSA-hf6r-mc9j-hf4p
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-discourse-2021-41271
Type: osv

## Affected
- Bitnami: `discourse` — affected unspecified

## Details
Discourse is a platform for community discussion. In affected versions a maliciously crafted request could cause an error response to be cached by intermediate proxies. This could cause a loss of confidentiality for some content. This issue is patched in the latest stable, beta and tests-passed versions of Discourse.

## References
- https://github.com/discourse/discourse/commit/2da0001965c6d8632d723c46ea5df9f22a1a23f1
- https://github.com/discourse/discourse/security/advisories/GHSA-hf6r-mc9j-hf4p
- https://nvd.nist.gov/vuln/detail/CVE-2021-41271
