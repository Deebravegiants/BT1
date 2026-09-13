# [H] Mastodon may allow unconfirmed FASP to make subscriptions

## Summary
Severity: High
Advisory: BIT-mastodon-2026-27468
Aliases: CVE-2026-27468, GHSA-qgmm-vr4c-ggjg
Ecosystem: Bitnami
Published: 2026-03-02
Source: https://osv.dev/vulnerability/BIT-mastodon-2026-27468
Type: osv

## Affected
- Bitnami: `mastodon` — affected >=4.5.0 <4.5.7

## Details
Mastodon is a free, open-source social network server based on ActivityPub. FASP registration requires manual approval by an administrator. In versions 4.4.0 through 4.4.13 and 4.5.0 through 4.5.6, actions performed by a FASP to subscribe to account/content lifecycle events or to backfill content did not check properly whether the FASP was actually approved. This only affects Mastodon servers that have opted in to testing the experimental FASP feature by setting the environment variable `EXPERIMENTAL_FEATURES` to a value including `fasp`. An attacker can make subscriptions and request content backfill without approval by an administrator. Done once, this leads to minor information leak of URIs that are publicly available anyway. But done several times this is a serious vector for DOS, putting pressure on the sidekiq worker responsible for the `fasp` queue. The fix is included in the 4.4.14 and 4.5.7 releases. Admins that are actively testing the experimental "fasp" feature should update their systems. Servers not using the experimental feature flag `fasp` are not affected.

## References
- https://github.com/mastodon/mastodon/commit/6ba6285a73c3a8b281123814d45f534e3bcebb96
- https://github.com/mastodon/mastodon/security/advisories/GHSA-qgmm-vr4c-ggjg
- https://nvd.nist.gov/vuln/detail/CVE-2026-27468
