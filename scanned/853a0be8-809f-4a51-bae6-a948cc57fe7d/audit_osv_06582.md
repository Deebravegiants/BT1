# [M] Mastodon has SSRF via unvalidated FASP Provider base_url

## Summary
Severity: Medium
Advisory: BIT-mastodon-2026-27477
Aliases: CVE-2026-27477, GHSA-46w6-g98f-wxqm
Ecosystem: Bitnami
Published: 2026-03-02
Source: https://osv.dev/vulnerability/BIT-mastodon-2026-27477
Type: osv

## Affected
- Bitnami: `mastodon` — affected >=4.5.0 <4.5.7

## Details
Mastodon is a free, open-source social network server based on ActivityPub. FASP registration requires manual approval by an administrator. In versions 4.4.0 through 4.4.13 and 4.5.0 through 4.5.6, an unauthenticated attacker can register a FASP with an attacker-chosen `base_url` that includes or resolves to a local / internal address, leading to the Mastodon server making requests to that address. This only affects Mastodon servers that have opted in to testing the experimental FASP feature by setting the environment variable `EXPERIMENTAL_FEATURES` to a value including `fasp`. An attacker can force the Mastodon server to make http(s) requests to internal systems. While they cannot control the full URL that is being requested (only the prefix) and cannot see the result of those requests, vulnerabilities or other undesired behavior could be triggered in those systems. The fix is included in the 4.4.14 and 4.5.7 releases. Admins that are actively testing the experimental "fasp" feature should update their systems. Servers not using the experimental feature flag `fasp` are not affected.

## References
- https://github.com/mastodon/mastodon/commit/7b85d2182361e68d51d9a02f94fb1070b5f503b1
- https://github.com/mastodon/mastodon/security/advisories/GHSA-46w6-g98f-wxqm
- https://nvd.nist.gov/vuln/detail/CVE-2026-27477
