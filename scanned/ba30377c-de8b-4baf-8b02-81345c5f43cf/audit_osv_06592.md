# [H] Mastodon: Exhausting data by an unauthenticated request to the admin retention API

## Summary
Severity: High
Advisory: BIT-mastodon-2026-72914
Aliases: CVE-2026-72914, GHSA-7jvv-fhmg-wpfw
Ecosystem: Bitnami
Published: 2026-08-17
Source: https://osv.dev/vulnerability/BIT-mastodon-2026-72914
Type: osv

## Affected
- Bitnami: `mastodon` — affected >=4.6.0 <4.6.4

## Details
Mastodon is a free, open-source social network server based on ActivityPub. Prior to 4.4.21, 4.5.14, 4.6.4, and 4.7.0, the administrative statistics endpoints handled by Api::V1::Admin::MeasuresController and Api::V1::Admin::RetentionController checked authorization only after beginning expensive calculations. Anonymous callers could submit keys, start_at, and end_at parameters that caused long-running SQL queries in Admin::Metrics::Measure, Admin::Metrics::Retention, and Admin::Metrics::Dimension::BaseDimension, allowing repeated requests to exhaust server resources. This issue is fixed in versions 4.4.21, 4.5.14, 4.6.4, and 4.7.0.

## References
- https://github.com/mastodon/mastodon/commit/18c61f286f1f5718a8f517940ba384866ffa3892
- https://github.com/mastodon/mastodon/commit/467c933459c7d0e5513475b9e4888afaedfb1074
- https://github.com/mastodon/mastodon/commit/930aa9fee26bf9eaefe27826fa1061288d83373b
- https://github.com/mastodon/mastodon/commit/da47a1bd3cd07935d7ca55a1f4f1a76f7f167e0d
- https://github.com/mastodon/mastodon/releases/tag/v4.4.21
- https://github.com/mastodon/mastodon/releases/tag/v4.5.14
- https://github.com/mastodon/mastodon/releases/tag/v4.6.4
- https://github.com/mastodon/mastodon/releases/tag/v4.7.0-beta.1
- https://github.com/mastodon/mastodon/security/advisories/GHSA-7jvv-fhmg-wpfw
- https://nvd.nist.gov/vuln/detail/CVE-2026-72914
