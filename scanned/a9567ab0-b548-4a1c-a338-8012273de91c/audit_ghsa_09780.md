# [M] Rack has a root directory disclosure via unescaped regex interpolation in Rack::Directory

## Summary
Severity: Medium
Advisory: GHSA-7mqq-6cf9-v2qp
CVE: CVE-2026-34763
CWE: CWE-625
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-04-02
Source: https://github.com/advisories/GHSA-7mqq-6cf9-v2qp
Type: github-advisory

## Affected
- RubyGems: `rack` — affected >=0 <2.2.23
- RubyGems: `rack` — affected >=3.0.0.beta1 <3.1.21
- RubyGems: `rack` — affected >=3.2.0 <3.2.6

## Details
## Summary

`Rack::Directory` interpolates the configured `root` path directly into a regular expression when deriving the displayed directory path. If `root` contains regex metacharacters such as `+`, `*`, or `.`, the prefix stripping can fail and the generated directory listing may expose the full filesystem path in the HTML output.

## Details

`Rack::Directory::DirectoryBody#each` computes the visible path using code equivalent to:

```ruby
show_path = Utils.escape_html(path.sub(/\A#{root}/, ''))
```

Here, `root` is a developer-configured filesystem path. It is normalized earlier with `File.expand_path(root)` and then inserted directly into a regular expression without escaping.

Because the value is treated as regex syntax rather than as a literal string, metacharacters in the configured path can change how the prefix match behaves. When that happens, the expected root prefix is not removed from `path`, and the absolute filesystem path is rendered into the HTML directory listing.

## Impact

If `Rack::Directory` is configured to serve a directory whose absolute path contains regex metacharacters, the generated directory listing may disclose the full server filesystem path instead of only the request-relative path.

This can expose internal deployment details such as directory layout, usernames, mount points, or naming conventions that would otherwise not be visible to clients.

## Mitigation

* Update to a patched version of Rack in which the root prefix is removed using an escaped regular expression.
* Avoid using `Rack::Directory` with a root path that contains regular expression metacharacters.

## References
- https://github.com/rack/rack/security/advisories/GHSA-7mqq-6cf9-v2qp
- https://nvd.nist.gov/vuln/detail/CVE-2026-34763
- https://github.com/rack/rack
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/rack/CVE-2026-34763.yml
