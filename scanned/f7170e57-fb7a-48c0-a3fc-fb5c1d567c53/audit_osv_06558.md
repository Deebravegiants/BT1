# [H] Mastodon vulnerable to Denial of Service through slow HTTP responses

## Summary
Severity: High
Advisory: BIT-mastodon-2023-36461
Aliases: CVE-2023-36461, GHSA-9pxv-6qvf-pjwc
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-mastodon-2023-36461
Type: osv

## Affected
- Bitnami: `mastodon` — affected >=4.1.0 <4.1.3

## Details
Mastodon is a free, open-source social network server based on ActivityPub. When performing outgoing HTTP queries, Mastodon sets a timeout on individual read operations. Prior to versions 3.5.9, 4.0.5, and 4.1.3, a malicious server can indefinitely extend the duration of the response through slowloris-type attacks. This vulnerability can be used to keep all Mastodon workers busy for an extended duration of time, leading to the server becoming unresponsive. Versions 3.5.9, 4.0.5, and 4.1.3 contain a patch for this issue.

## References
- http://www.openwall.com/lists/oss-security/2023/07/06/7
- https://github.com/mastodon/mastodon/commit/c5929798bf7e56cc2c79b15bed0c4692ded3dcb6
- https://github.com/mastodon/mastodon/releases/tag/v3.5.9
- https://github.com/mastodon/mastodon/releases/tag/v4.0.5
- https://github.com/mastodon/mastodon/releases/tag/v4.1.3
- https://github.com/mastodon/mastodon/security/advisories/GHSA-9pxv-6qvf-pjwc
- https://nvd.nist.gov/vuln/detail/CVE-2023-36461
