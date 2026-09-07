# [H] Rack: Multipart parser buffers large non‑file fields entirely in memory, enabling DoS (memory exhaustion)

## Summary
Severity: High
Advisory: GHSA-w9pc-fmgc-vxvw
CVE: CVE-2025-61771
CWE: CWE-400
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-10-07
Source: https://github.com/advisories/GHSA-w9pc-fmgc-vxvw
Type: github-advisory

## Affected
- RubyGems: `rack` — affected >=0 <2.2.19
- RubyGems: `rack` — affected >=3.1 <3.1.17
- RubyGems: `rack` — affected >=3.2 <3.2.2

## Details
## Summary

`Rack::Multipart::Parser` stores non-file form fields (parts without a `filename`) entirely in memory as Ruby `String` objects. A single large text field in a multipart/form-data request (hundreds of megabytes or more) can consume equivalent process memory, potentially leading to out-of-memory (OOM) conditions and denial of service (DoS).

## Details

During multipart parsing, file parts are streamed to temporary files, but non-file parts are buffered into memory:

```ruby
body = String.new  # non-file → in-RAM buffer
@mime_parts[mime_index].body << content
```

There is no size limit on these in-memory buffers. As a result, any large text field—while technically valid—will be loaded fully into process memory before being added to `params`.

## Impact

Attackers can send large non-file fields to trigger excessive memory usage. Impact scales with request size and concurrency, potentially leading to worker crashes or severe garbage-collection overhead. All Rack applications processing multipart form submissions are affected.

## Mitigation

* **Upgrade:** Use a patched version of Rack that enforces a reasonable size cap for non-file fields (e.g., 2 MiB).
* **Workarounds:**
  * Restrict maximum request body size at the web-server or proxy layer (e.g., Nginx `client_max_body_size`).
  * Validate and reject unusually large form fields at the application level.

## References
- https://github.com/rack/rack/security/advisories/GHSA-w9pc-fmgc-vxvw
- https://nvd.nist.gov/vuln/detail/CVE-2025-61771
- https://github.com/rack/rack/commit/589127f4ac8b5cf11cf88fb0cd116ffed4d2181e
- https://github.com/rack/rack/commit/d869fed663b113b95a74ad53e1b5cae6ab31f29e
- https://github.com/rack/rack/commit/e08f78c656c9394d6737c022bde087e0f33336fd
- https://github.com/rack/rack
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/rack/CVE-2025-61771.yml
