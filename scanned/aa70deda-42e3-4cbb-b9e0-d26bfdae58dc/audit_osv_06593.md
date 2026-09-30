# [H] Mastodon: Personally-identifying information disclosure due to incorrect access control validation

## Summary
Severity: High
Advisory: BIT-mastodon-2026-72915
Aliases: CVE-2026-72915, GHSA-hx34-2pfw-2qfj
Ecosystem: Bitnami
Published: 2026-08-17
Source: https://osv.dev/vulnerability/BIT-mastodon-2026-72915
Type: osv

## Affected
- Bitnami: `mastodon` — affected >=4.6.0 <4.6.4

## Details
Mastodon is a free, open-source social network server based on ActivityPub. From 4.6.0 until 4.6.4 and 4.7.0, any logged-in local user could use the show action in app/controllers/admin/collections_controller.rb to access personally identifying information about another local user in a collection because the controller used the general collection policy instead of the admin collection policy namespace. The exposed data included the other user's current email address and last-used IP address. This issue is fixed in versions 4.6.4 and 4.7.0.

## References
- https://github.com/mastodon/mastodon/commit/467c933459c7d0e5513475b9e4888afaedfb1074
- https://github.com/mastodon/mastodon/commit/930aa9fee26bf9eaefe27826fa1061288d83373b
- https://github.com/mastodon/mastodon/releases/tag/v4.6.4
- https://github.com/mastodon/mastodon/releases/tag/v4.7.0-beta.1
- https://github.com/mastodon/mastodon/security/advisories/GHSA-hx34-2pfw-2qfj
- https://nvd.nist.gov/vuln/detail/CVE-2026-72915
