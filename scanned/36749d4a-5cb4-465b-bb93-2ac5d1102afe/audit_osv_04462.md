# [H] Discourse users are able to see their own whispers even after being removed from a group that has been configured to see whispers

## Summary
Severity: High
Advisory: BIT-discourse-2025-49845
Aliases: CVE-2025-49845, GHSA-79qw-r73r-69gf
Ecosystem: Bitnami
Published: 2025-07-01
Source: https://osv.dev/vulnerability/BIT-discourse-2025-49845
Type: osv

## Affected
- Bitnami: `discourse` — affected >=0 <3.4.6

## Details
Discourse is an open-source discussion platform. The visibility of posts typed `whisper` is controlled via the `whispers_allowed_groups` site setting. Only users that belong to groups specified in the site setting are allowed to view posts typed `whisper`. However, it has been discovered that users of versions prior to 3.4.6 on the `stable` branch and prior to 3.5.0.beta8-dev on the `tests-passed` branch can continue to see their own whispers even after losing visibility of posts typed `whisper`. This issue is patched in versions 3.4.6 and 3.5.0.beta8-dev. No known workarounds are available.

## References
- https://github.com/discourse/discourse/security/advisories/GHSA-79qw-r73r-69gf
- https://nvd.nist.gov/vuln/detail/CVE-2025-49845
