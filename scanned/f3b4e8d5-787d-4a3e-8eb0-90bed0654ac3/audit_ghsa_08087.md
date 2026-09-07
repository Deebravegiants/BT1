# [H] Phlex XSS protection bypass via attribute splatting, dynamic tags, and href values

## Summary
Severity: High
Advisory: GHSA-w67g-2h6v-vjgq
CWE: CWE-79
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2026-02-06
Source: https://github.com/advisories/GHSA-w67g-2h6v-vjgq
Type: github-advisory

## Affected
- RubyGems: `phlex` — affected >=2.4.0.beta1 <2.4.1
- RubyGems: `phlex` — affected >=2.3.0 <2.3.2
- RubyGems: `phlex` — affected >=2.2.0 <2.2.2
- RubyGems: `phlex` — affected >=2.1.0 <2.1.3
- RubyGems: `phlex` — affected >=2.0.0.beta1 <2.0.2
- RubyGems: `phlex` — affected >=0 <1.11.1

## Details
### Impact

During a security audit conducted with Claude Opus 4.6 and GPT-5.3-Codex, we identified three specific ways to bypass the XSS (cross-site-scripting) protection built into Phlex.

1. The first bypass could happen if user-provided attributes with string keys were splatted into HTML tag, e.g. `div(**user_attributes)`.
2. The second bypass could happen if user-provided tag names were passed to the `tag` method, e.g. `tag(some_tag_name_from_user)`.
3. The third bypass could happen if user’s links were passed to `href` attributes, e.g. `a(href: user_provided_link)`.

All three of these patterns are meant to be safe and all have now been patched.

### Patches

Phlex has patched all three issues and introduced new tests that run against Safari, Firefox and Chrome.

The patched versions are:

- [2.4.1](https://rubygems.org/gems/phlex/versions/2.4.1)
- [2.3.2](https://rubygems.org/gems/phlex/versions/2.3.2)
- [2.2.2](https://rubygems.org/gems/phlex/versions/2.2.2)
- [2.1.3](https://rubygems.org/gems/phlex/versions/2.1.3)
- [2.0.2](https://rubygems.org/gems/phlex/versions/2.0.3)
- [1.11.1](https://rubygems.org/gems/phlex/versions/1.11.1)

Phlex has also patched the [`main`](https://github.com/yippee-fun/phlex) branch in GitHub.

### Workarounds
If a project uses a secure CSP (content security policy) or if the application doesn’t use any of the above patterns, it is not at risk.

## References
- https://github.com/yippee-fun/phlex/security/advisories/GHSA-w67g-2h6v-vjgq
- https://github.com/yippee-fun/phlex/commit/1d85da417cb15eb8cb2f54a68d531c9b35d9d03a
- https://github.com/yippee-fun/phlex/commit/556441d5a64ff93f749e8116a05b2d97264468ee
- https://github.com/yippee-fun/phlex/commit/74e3d8610ffabc2cf5f241945e9df4b14dceb97d
- https://github.com/yippee-fun/phlex/commit/9f56ad13bea9a7d6117fdfd510446c890709eeac
- https://github.com/yippee-fun/phlex/commit/fe9ea708672f9fa42526d9b47e1cdc4634860ef1
- https://github.com/yippee-fun/phlex
