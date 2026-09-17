# [H] Lack of media type verification of Activity Streams objects allows impersonation of remote accounts

## Summary
Severity: High
Advisory: BIT-mastodon-2024-25623
Aliases: CVE-2024-25623, GHSA-jhrq-qvrm-qr36
Ecosystem: Bitnami
Published: 2024-03-31
Source: https://osv.dev/vulnerability/BIT-mastodon-2024-25623
Type: osv

## Affected
- Bitnami: `mastodon` — affected >=4.2.0 <4.2.7

## Details
Mastodon is a free, open-source social network server based on ActivityPub. Prior to versions 4.2.7, 4.1.15, 4.0.15, and 3.5.19, when fetching remote statuses, Mastodon doesn't check that the response from the remote server has a `Content-Type` header value of the Activity Streams media type, which allows a threat actor to upload a crafted Activity Streams document to a remote server and make a Mastodon server fetch it, if the remote server accepts arbitrary user uploads. The vulnerability allows a threat actor to impersonate an account on a remote server that satisfies all of the following properties: allows the attacker to register an account; accepts arbitrary user-uploaded documents and places them on the same domain as the ActivityPub actors; and serves user-uploaded document in response to requests with an `Accept` header value of the Activity Streams media type. Versions 4.2.7, 4.1.15, 4.0.15, and 3.5.19 contain a fix for this issue.

## References
- https://github.com/mastodon/mastodon/commit/9fee5e852669e26f970e278021302e1a203fc022
- https://github.com/mastodon/mastodon/security/advisories/GHSA-jhrq-qvrm-qr36
- https://nvd.nist.gov/vuln/detail/CVE-2024-25623
