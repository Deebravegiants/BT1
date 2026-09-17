# [M] Discourse vulnerable to DoS via drafts

## Summary
Severity: Medium
Advisory: BIT-discourse-2023-38706
Aliases: CVE-2023-38706, GHSA-7wpp-4pqg-gvp8
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-discourse-2023-38706
Type: osv

## Affected
- Bitnami: `discourse` — affected >=0 <3.1.1

## Details
Discourse is an open-source discussion platform. Prior to version 3.1.1 of the `stable` branch, a malicious user can create an unlimited number of drafts with very long draft keys which may end up exhausting the resources on the server. The issue is patched in version 3.1.1 of the `stable` branch. There are no known workarounds.

## References
- https://github.com/discourse/discourse/security/advisories/GHSA-7wpp-4pqg-gvp8
- https://nvd.nist.gov/vuln/detail/CVE-2023-38706
