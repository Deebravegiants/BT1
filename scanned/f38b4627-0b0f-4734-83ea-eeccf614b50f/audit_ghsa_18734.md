# [H] Rack is vulnerable to a memory-exhaustion DoS through unbounded URL-encoded body parsing

## Summary
Severity: High
Advisory: GHSA-6xw4-3v39-52mm
CVE: CVE-2025-61919
CWE: CWE-400
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-10-10
Source: https://github.com/advisories/GHSA-6xw4-3v39-52mm
Type: github-advisory

## Affected
- RubyGems: `rack` — affected >=0 <2.2.20
- RubyGems: `rack` — affected >=3.0 <3.1.18
- RubyGems: `rack` — affected >=3.2 <3.2.3

## Details
## Summary

`Rack::Request#POST` reads the entire request body into memory for `Content-Type: application/x-www-form-urlencoded`, calling `rack.input.read(nil)` without enforcing a length or cap. Large request bodies can therefore be buffered completely into process memory before parsing, leading to denial of service (DoS) through memory exhaustion.

## Details

When handling non-multipart form submissions, Rack’s request parser performs:

```ruby
form_vars = get_header(RACK_INPUT).read
```

Since `read` is called with no argument, the entire request body is loaded into a Ruby `String`. This occurs before query parameter parsing or enforcement of any `params_limit`. As a result, Rack applications without an upstream body-size limit can experience unbounded memory allocation proportional to request size.

## Impact

Attackers can send large `application/x-www-form-urlencoded` bodies to consume process memory, causing slowdowns or termination by the operating system (OOM). The effect scales linearly with request size and concurrency. Even with parsing limits configured, the issue occurs *before* those limits are enforced.

## Mitigation

* Update to a patched version of Rack that enforces form parameter limits using `query_parser.bytesize_limit`, preventing unbounded reads of `application/x-www-form-urlencoded` bodies.
* Enforce strict maximum body size at the proxy or web server layer (e.g., Nginx `client_max_body_size`, Apache `LimitRequestBody`).

## References
- https://github.com/rack/rack/security/advisories/GHSA-6xw4-3v39-52mm
- https://nvd.nist.gov/vuln/detail/CVE-2025-61919
- https://github.com/rack/rack/commit/4e2c903991a790ee211a3021808ff4fd6fe82881
- https://github.com/rack/rack/commit/cbd541e8a3d0c5830a3c9a30d3718ce2e124f9db
- https://github.com/rack/rack/commit/e179614c4a653283286f5f046428cbb85f21146f
- https://github.com/rack/rack
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/rack/CVE-2025-61919.yml
