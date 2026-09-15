# [C] graphql allows remote code execution when loading a crafted GraphQL schema

## Summary
Severity: Critical
Advisory: GHSA-q92j-grw3-h492
CVE: CVE-2025-27407
CWE: CWE-94
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2025-03-12
Source: https://github.com/advisories/GHSA-q92j-grw3-h492
Type: github-advisory

## Affected
- RubyGems: `graphql` — affected >=2.4.0 <2.4.13
- RubyGems: `graphql` — affected >=2.3.0 <2.3.21
- RubyGems: `graphql` — affected >=2.2.0 <2.2.17
- RubyGems: `graphql` — affected >=2.1.0 <2.1.15
- RubyGems: `graphql` — affected >=2.0.0 <2.0.32
- RubyGems: `graphql` — affected >=1.13.0 <1.13.24
- RubyGems: `graphql` — affected >=1.12.0 <1.12.25
- RubyGems: `graphql` — affected >=1.11.5 <1.11.11

## Details
# Summary

Loading a malicious schema definition in `GraphQL::Schema.from_introspection` (or `GraphQL::Schema::Loader.load`) can result in remote code execution. Any system which loads a schema by JSON from an untrusted source is vulnerable, including those that use [GraphQL::Client](https://github.com/github-community-projects/graphql-client) to load external schemas via GraphQL introspection.

## References
- https://github.com/rmosolgo/graphql-ruby/security/advisories/GHSA-q92j-grw3-h492
- https://nvd.nist.gov/vuln/detail/CVE-2025-27407
- https://github.com/rmosolgo/graphql-ruby/commit/28233b16c0eb9d0fb7808f4980e061dc7507c4cd
- https://github.com/rmosolgo/graphql-ruby/commit/2d2f4ed1f79472f8eed29c864b039649e1de238f
- https://github.com/rmosolgo/graphql-ruby/commit/5c5a7b9a9bdce143be048074aea50edb7bb747be
- https://github.com/rmosolgo/graphql-ruby/commit/6eca16b9fa553aa957099a30dbde64ddcdac52ca
- https://github.com/rmosolgo/graphql-ruby/commit/d0963289e0dab4ea893bbecf12bb7d89294957bb
- https://github.com/rmosolgo/graphql-ruby/commit/d1117ae0361d9ed67e0795b07f5c3e98e62f3c7c
- https://github.com/rmosolgo/graphql-ruby/commit/e3b33ace05391da2871c75ab4d3b66e29133b367
- https://github.com/rmosolgo/graphql-ruby/commit/e58676c70aa695e3052ba1fbc787efee4ba7d67e
- https://about.gitlab.com/releases/2025/03/12/patch-release-gitlab-17-9-2-released
- https://github.com/github-community-projects/graphql-client
- https://github.com/rmosolgo/graphql-ruby
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/graphql/CVE-2025-27407.yml
- https://lists.debian.org/debian-lts-announce/2025/08/msg00002.html
