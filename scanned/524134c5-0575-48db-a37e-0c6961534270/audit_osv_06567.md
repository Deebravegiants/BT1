# [H] Mastodon has improper authorship check on audience extension for existing posts

## Summary
Severity: High
Advisory: BIT-mastodon-2024-37903
Aliases: CVE-2024-37903, GHSA-xjvf-fm67-4qc3
Ecosystem: Bitnami
Published: 2024-07-09
Source: https://osv.dev/vulnerability/BIT-mastodon-2024-37903
Type: osv

## Affected
- Bitnami: `mastodon` — affected >=4.2.0 <4.2.10

## Details
Mastodon is a self-hosted, federated microblogging platform. Starting in version 2.6.0 and prior to versions 4.1.18 and 4.2.10, by crafting specific activities, an attacker can extend the audience of a post they do not own to other Mastodon users on a target server, thus gaining access to the contents of a post not intended for them. Versions 4.1.18 and 4.2.10 contain a patch for this issue.

## References
- https://github.com/mastodon/mastodon/commit/a1c7aae28aecf06659c5b18cfa131b37cd1512a3
- https://github.com/mastodon/mastodon/commit/d4bf22b632ea8b1174375c4966a6768ab66393b6
- https://github.com/mastodon/mastodon/releases/tag/v4.1.18
- https://github.com/mastodon/mastodon/releases/tag/v4.2.10
- https://github.com/mastodon/mastodon/security/advisories/GHSA-xjvf-fm67-4qc3
- https://nvd.nist.gov/vuln/detail/CVE-2024-37903
