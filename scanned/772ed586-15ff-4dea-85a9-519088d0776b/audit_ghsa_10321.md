# [H] Rack::Static prefix matching can expose unintended files under the static root

## Summary
Severity: High
Advisory: GHSA-h2jq-g4cq-5ppq
CVE: CVE-2026-34785
CWE: CWE-187, CWE-200
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-04-02
Source: https://github.com/advisories/GHSA-h2jq-g4cq-5ppq
Type: github-advisory

## Affected
- RubyGems: `rack` — affected >=0 <2.2.23
- RubyGems: `rack` — affected >=3.0.0.beta1 <3.1.21
- RubyGems: `rack` — affected >=3.2.0 <3.2.6

## Details
## Summary

`Rack::Static` determines whether a request should be served as a static file using a simple string prefix check. When configured with URL prefixes such as `"/css"`, it matches any request path that begins with that string, including unrelated paths such as `"/css-config.env"` or `"/css-backup.sql"`.

As a result, files under the static root whose names merely share the configured prefix may be served unintentionally, leading to information disclosure.

## Details

`Rack::Static#route_file` performs static-route matching using logic equivalent to:

```ruby
@urls.any? { |url| path.index(url) == 0 }
```

This checks only whether the request path starts with the configured prefix string. It does not require a path segment boundary after the prefix.

For example, with:

```ruby
use Rack::Static, urls: ["/css", "/js"], root: "public"
```

the following path is matched as intended:

```text
/css/style.css
```

but these paths are also matched:

```text
/css-config.env
/css-backup.sql
/csssecrets.yml
```

If such files exist under the configured static root, Rack forwards the request to the file server and serves them as static content.

This means a configuration intended to expose only directory trees such as `/css/...` and `/js/...` may also expose sibling files whose names begin with those same strings.

## Impact

An attacker can request files under the configured static root whose names share a configured URL prefix and obtain their contents.

In affected deployments, this may expose configuration files, secrets, backups, environment files, or other unintended static content located under the same root directory.

## Mitigation

* Update to a patched version of Rack that enforces a path boundary when matching configured static URL prefixes.
* Match only paths that are either exactly equal to the configured prefix or begin with `prefix + "/"`.
* Avoid placing sensitive files under the `Rack::Static` root directory.
* Prefer static URL mappings that cannot overlap with sensitive filenames.

## References
- https://github.com/rack/rack/security/advisories/GHSA-h2jq-g4cq-5ppq
- https://nvd.nist.gov/vuln/detail/CVE-2026-34785
- https://github.com/rack/rack
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/rack/CVE-2026-34785.yml
