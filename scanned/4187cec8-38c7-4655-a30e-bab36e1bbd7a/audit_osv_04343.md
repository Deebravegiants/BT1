# [M] Bypass of Poll voting limits in Discourse

## Summary
Severity: Medium
Advisory: BIT-discourse-2021-43793
Aliases: CVE-2021-43793, GHSA-jq7h-44vc-h6qx
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-discourse-2021-43793
Type: osv

## Affected
- Bitnami: `discourse` — affected >=0 <2.7.11

## Details
Discourse is an open source discussion platform. In affected versions a vulnerability in the Polls feature allowed users to vote multiple times in a single-option poll. The problem is patched in the latest tests-passed, beta and stable versions of Discourse

## References
- https://github.com/discourse/discourse/commit/0c6b9df77bac9c6f7c7e2eadf6fe100064afdeab
- https://github.com/discourse/discourse/commit/1d0faedfbc3a8b77b971dc70d25e30791dbb6e0b
- https://github.com/discourse/discourse/security/advisories/GHSA-jq7h-44vc-h6qx
- https://nvd.nist.gov/vuln/detail/CVE-2021-43793
