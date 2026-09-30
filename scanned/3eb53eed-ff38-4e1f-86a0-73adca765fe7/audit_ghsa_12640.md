# [M] Doorkeeper Improper Authentication vulnerability

## Summary
Severity: Medium
Advisory: GHSA-7w2c-w47h-789w
CVE: CVE-2023-34246
CWE: CWE-287
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2023-06-12
Source: https://github.com/advisories/GHSA-7w2c-w47h-789w
Type: github-advisory

## Affected
- RubyGems: `doorkeeper` — affected >=0 <5.6.6

## Details
OAuth RFC 8252 says  https://www.rfc-editor.org/rfc/rfc8252#section-8.6

> the authorization server SHOULD NOT process authorization requests automatically without user consent or interaction, except when the identity of the client can be assured. **This includes the case where the user has previously approved an authorization request for a given client id**

But Doorkeeper automatically processes authorization requests without user consent for public clients that have been previously approved. Public clients are inherently vulnerable to impersonation, their identity cannot be assured.

Issue https://github.com/doorkeeper-gem/doorkeeper/issues/1589

Fix https://github.com/doorkeeper-gem/doorkeeper/pull/1646

## References
- https://github.com/doorkeeper-gem/doorkeeper/security/advisories/GHSA-7w2c-w47h-789w
- https://nvd.nist.gov/vuln/detail/CVE-2023-34246
- https://github.com/doorkeeper-gem/doorkeeper/issues/1589
- https://github.com/doorkeeper-gem/doorkeeper/pull/1646
- https://github.com/doorkeeper-gem/doorkeeper
- https://github.com/doorkeeper-gem/doorkeeper/releases/tag/v5.6.6
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/doorkeeper/CVE-2023-34246.yml
- https://lists.debian.org/debian-lts-announce/2023/07/msg00016.html
- https://lists.debian.org/debian-lts-announce/2024/12/msg00010.html
- https://www.rfc-editor.org/rfc/rfc8252#section-8.6
