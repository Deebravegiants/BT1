# [H] Rack's multipart parser buffers unbounded per-part headers, enabling DoS (memory exhaustion)

## Summary
Severity: High
Advisory: GHSA-wpv5-97wm-hp9c
CVE: CVE-2025-61772
CWE: CWE-400
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-10-07
Source: https://github.com/advisories/GHSA-wpv5-97wm-hp9c
Type: github-advisory

## Affected
- RubyGems: `rack` — affected >=0 <2.2.19
- RubyGems: `rack` — affected >=3.1 <3.1.17
- RubyGems: `rack` — affected >=3.2 <3.2.2

## Details
## Summary

`Rack::Multipart::Parser` can accumulate unbounded data when a multipart part’s header block never terminates with the required blank line (`CRLFCRLF`). The parser keeps appending incoming bytes to memory without a size cap, allowing a remote attacker to exhaust memory and cause a denial of service (DoS).

## Details

While reading multipart headers, the parser waits for `CRLFCRLF` using:

```ruby
@sbuf.scan_until(/(.*?\r\n)\r\n/m)
```

If the terminator never appears, it continues appending data (`@sbuf.concat(content)`) indefinitely. There is no limit on accumulated header bytes, so a single malformed part can consume memory proportional to the request body size.

## Impact

Attackers can send incomplete multipart headers to trigger high memory use, leading to process termination (OOM) or severe slowdown. The effect scales with request size limits and concurrency. All applications handling multipart uploads may be affected.

## Mitigation

* Upgrade to a patched Rack version that caps per-part header size (e.g., 64 KiB).
* Until then, restrict maximum request sizes at the proxy or web server layer (e.g., Nginx `client_max_body_size`).

## References
- https://github.com/rack/rack/security/advisories/GHSA-wpv5-97wm-hp9c
- https://nvd.nist.gov/vuln/detail/CVE-2025-61772
- https://github.com/rack/rack/commit/589127f4ac8b5cf11cf88fb0cd116ffed4d2181e
- https://github.com/rack/rack/commit/d869fed663b113b95a74ad53e1b5cae6ab31f29e
- https://github.com/rack/rack/commit/e08f78c656c9394d6737c022bde087e0f33336fd
- https://github.com/rack/rack
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/rack/CVE-2025-61772.yml
