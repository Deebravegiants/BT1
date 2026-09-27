# [M] Mastodon missing length limits on list names, filter names, and filter keywords

## Summary
Severity: Medium
Advisory: BIT-mastodon-2026-23963
Aliases: CVE-2026-23963, GHSA-6x3w-9g92-gvf3
Ecosystem: Bitnami
Published: 2026-02-03
Source: https://osv.dev/vulnerability/BIT-mastodon-2026-23963
Type: osv

## Affected
- Bitnami: `mastodon` — affected >=4.5.0 <4.5.5

## Details
Mastodon is a free, open-source social network server based on ActivityPub. Prior to versions 4.5.5, 4.4.12, and 4.3.18, the server does not enforce a maximum length for the names of lists or filters, or for filter keywords, allowing any user to set an arbitrarily long string as the name or keyword. Any local user can abuse the list or filter fields to cause disproportionate storage and computing resource usage. They can additionally cause their own web interface to be unusable, although they must intentionally do this to themselves or unknowingly approve a malicious API client. Mastodon versions v4.5.5, v4.4.12, v4.3.18 are patched.

## References
- https://github.com/mastodon/mastodon/releases/tag/v4.3.18
- https://github.com/mastodon/mastodon/releases/tag/v4.4.12
- https://github.com/mastodon/mastodon/releases/tag/v4.5.5
- https://github.com/mastodon/mastodon/security/advisories/GHSA-6x3w-9g92-gvf3
- https://nvd.nist.gov/vuln/detail/CVE-2026-23963
