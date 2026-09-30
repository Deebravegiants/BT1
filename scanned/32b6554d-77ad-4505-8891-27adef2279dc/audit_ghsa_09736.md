# [H] Rack's multipart parsing without Content-Length header allows unbounded chunked file uploads

## Summary
Severity: High
Advisory: GHSA-8vqr-qjwx-82mw
CVE: CVE-2026-34829
CWE: CWE-400, CWE-770
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-04-02
Source: https://github.com/advisories/GHSA-8vqr-qjwx-82mw
Type: github-advisory

## Affected
- RubyGems: `rack` — affected >=0 <2.2.23
- RubyGems: `rack` — affected >=3.0.0.beta1 <3.1.21
- RubyGems: `rack` — affected >=3.2.0 <3.2.6

## Details
## Summary

`Rack::Multipart::Parser` only wraps the request body in a `BoundedIO` when `CONTENT_LENGTH` is present. When a `multipart/form-data` request is sent without a `Content-Length` header, such as with HTTP chunked transfer encoding, multipart parsing continues until end-of-stream with no total size limit.

For file parts, the uploaded body is written directly to a temporary file on disk rather than being constrained by the buffered in-memory upload limit. An unauthenticated attacker can therefore stream an arbitrarily large multipart file upload and consume unbounded disk space.

This results in a denial of service condition for Rack applications that accept multipart form data.

## Details

`Rack::Multipart::Parser.parse` applies `BoundedIO` only when `content_length` is not `nil`:

```ruby
io = BoundedIO.new(io, content_length) if content_length
```

When `CONTENT_LENGTH` is absent, the parser reads the multipart body until EOF without a global byte limit.

Although Rack enforces `BUFFERED_UPLOAD_BYTESIZE_LIMIT` for retained non-file parts, file uploads are handled differently. When a multipart part includes a filename, the body is streamed to a `Tempfile`, and the retained-size accounting is not applied to that file content. As a result, file parts are not subject to the same upload size bound.

An attacker can exploit this by sending a chunked `multipart/form-data` request containing a file part and continuously streaming data without declaring a `Content-Length`. Rack will continue writing the uploaded data to disk until the client stops or the server exhausts available storage.

## Impact

Any Rack application that accepts `multipart/form-data` uploads may be affected if no upstream component enforces a request body size limit.

An unauthenticated attacker can send a large chunked file upload to consume disk space on the application host. This may cause request failures, application instability, or broader service disruption if the host runs out of available storage.

The practical impact depends on deployment architecture. Reverse proxies or application servers that enforce upload limits may reduce or eliminate exploitability, but Rack itself does not impose a total multipart upload limit in this code path when `CONTENT_LENGTH` is absent.

## Mitigation

* Update to a patched version of Rack that enforces a total multipart upload size limit even when `CONTENT_LENGTH` is absent.
* Enforce request body size limits at the reverse proxy or application server.
* Isolate temporary upload storage and monitor disk consumption for multipart endpoints.

## References
- https://github.com/rack/rack/security/advisories/GHSA-8vqr-qjwx-82mw
- https://nvd.nist.gov/vuln/detail/CVE-2026-34829
- https://github.com/rack/rack
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/rack/CVE-2026-34829.yml
