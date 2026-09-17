# [M] GraphQL-Ruby's Ruby lexer does not count comment tokens for the purposes of max_query_string_tokens

## Summary
Severity: Medium
Advisory: GHSA-3h96-34p3-xm76
CWE: CWE-770
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-05-05
Source: https://github.com/advisories/GHSA-3h96-34p3-xm76
Type: github-advisory

## Affected
- RubyGems: `graphql` — affected >=2.6.0 <2.6.1
- RubyGems: `graphql` — affected >=2.5.0 <2.5.26
- RubyGems: `graphql` — affected >=2.4.0 <2.4.18
- RubyGems: `graphql` — affected >=2.3.1 <2.3.23

## Details
GraphQL-Ruby's `max_query_string_tokens` configuration didn't count comment tokens against the limit, allowing strings to be processed even after the configured maximum had actually been reached. 

In patched versions, the Ruby lexer does count these tokens. 

GraphQL-CParser is not affected by this problem. 

`max_query_string_tokens` was introduced in v2.3.1. Each 2.x version has received a new patch release for including a fix.

## References
- https://github.com/rmosolgo/graphql-ruby/security/advisories/GHSA-3h96-34p3-xm76
- https://github.com/rmosolgo/graphql-ruby
