# [H] Mastodon has a consent-check bypass in its remote Collections

## Summary
Severity: High
Advisory: BIT-mastodon-2026-47777
Aliases: CVE-2026-47777, GHSA-vg36-gxjg-2v46
Ecosystem: Bitnami
Published: 2026-06-18
Source: https://osv.dev/vulnerability/BIT-mastodon-2026-47777
Type: osv

## Affected
- Bitnami: `mastodon` — affected >=nightly.2026-03-10.0 <4.6.0

## Details
Mastodon is a free, open-source social network server based on ActivityPub. In versions there is a missing condition in the check if remote accounts consented to be featured in a remote Collection could lead to attackers bypassing the check and faking consent. An attacker could forge the FeatureAuthorization object that is used to verify consent to be featured in a Collection and thus make it appear as if an account is allowed to be in a Collection when it actually is not. While the FeatureAuthorization must reside on the same domain as the object it is for, a check is missing to make sure said object is actually the same as in the Collection item. This allows an attacker to forge the authorization. Mastodon servers are affected only if running the main branch or nightly builds who have opted into testing the experimental "Collections" feature by setting the environment variable EXPERIMENTAL_FEATURES to a value including collections. This has been patched in version 4.6.0.

## References
- https://github.com/mastodon/mastodon/commit/22203f8aeb03e8f14dc62e253e83db39825a5bcf
- https://github.com/mastodon/mastodon/security/advisories/GHSA-vg36-gxjg-2v46
- https://nvd.nist.gov/vuln/detail/CVE-2026-47777
