# [H] Rack has a Directory Traversal via Rack:Directory

## Summary
Severity: High
Advisory: GHSA-mxw3-3hh2-x2mh
CVE: CVE-2026-22860
CWE: CWE-22, CWE-548
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-02-17
Source: https://github.com/advisories/GHSA-mxw3-3hh2-x2mh
Type: github-advisory

## Affected
- RubyGems: `rack` — affected >=0 <2.2.22
- RubyGems: `rack` — affected >=3.0.0.beta1 <3.1.20
- RubyGems: `rack` — affected >=3.2.0 <3.2.5

## Details
## Summary

`Rack::Directory`’s path check used a string prefix match on the expanded path. A request like `/../root_example/` can escape the configured root if the target path starts with the root string, allowing directory listing outside the intended root.

## Details

In `directory.rb`, `File.expand_path(File.join(root, path_info)).start_with?(root)` does not enforce a path boundary. If the server root is `/var/www/root`, a path like `/var/www/root_backup` passes the check because it shares the same prefix, so `Rack::Directory` will list that directory also. 

## Impact

Information disclosure via directory listing outside the configured root when `Rack::Directory` is exposed to untrusted clients and a directory shares the root prefix (e.g., `public2`, `www_backup`).

## Mitigation

* Update to a patched version of Rack that correctly checks the root prefix.
* Don't name directories with the same prefix as one which is exposed via `Rack::Directory`.

## References
- https://github.com/rack/rack/security/advisories/GHSA-mxw3-3hh2-x2mh
- https://nvd.nist.gov/vuln/detail/CVE-2026-22860
- https://github.com/rack/rack/commit/75c5745c286637a8f049a33790c71237762069e7
- https://github.com/rack/rack
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/rack/CVE-2026-22860.yml
