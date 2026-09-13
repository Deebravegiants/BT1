# [H] Mastodon Server-Side Request Forgery vulnerability

## Summary
Severity: High
Advisory: BIT-mastodon-2023-42450
Aliases: CVE-2023-42450, GHSA-hcqf-fw2r-52g4
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-mastodon-2023-42450
Type: osv

## Affected
- Bitnami: `mastodon` — affected >=4.2.0-rc1 <4.2.0

## Details
Mastodon is a free, open-source social network server based on ActivityPub. Starting in version 4.2.0-beta1 and prior to version 4.2.0-rc2, by crafting specific input, attackers can inject arbitrary data into HTTP requests issued by Mastodon. This can be used to perform confused deputy attacks if the server configuration includes `ALLOWED_PRIVATE_ADDRESSES` to allow access to local exploitable services. Version 4.2.0-rc2 has a patch for the issue.

## References
- https://github.com/mastodon/mastodon/commit/94893cf24fc95b32cc7a756262acbe008c20a9d2
- https://github.com/mastodon/mastodon/security/advisories/GHSA-hcqf-fw2r-52g4
- https://nvd.nist.gov/vuln/detail/CVE-2023-42450
