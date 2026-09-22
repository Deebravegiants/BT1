# [M] Mastodon's rate-limits are missing on `/auth/setup`

## Summary
Severity: Medium
Advisory: BIT-mastodon-2025-27157
Aliases: CVE-2025-27157, GHSA-v39f-c9jj-8w7h
Ecosystem: Bitnami
Published: 2025-03-02
Source: https://osv.dev/vulnerability/BIT-mastodon-2025-27157
Type: osv

## Affected
- Bitnami: `mastodon` — affected >=4.2.0 <4.3.4

## Details
Mastodon is a self-hosted, federated microblogging platform. Starting in version 4.2.0 and prior to versions 4.2.16 and 4.3.4, the rate limits are missing on `/auth/setup`. Without those rate limits, an attacker can craft requests that will send an email to an arbitrary addresses. Versions 4.2.16 and 4.3.4 fix the issue.

## References
- https://github.com/mastodon/mastodon/commit/06f879ce9bea195344ac9f71e6799eea500628ec
- https://github.com/mastodon/mastodon/security/advisories/GHSA-v39f-c9jj-8w7h
- https://nvd.nist.gov/vuln/detail/CVE-2025-27157
