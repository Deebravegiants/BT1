# [M] CVE-2021-32715

## Summary
Severity: Medium
Advisory: CVE-2021-32715
Aliases: GHSA-f3pg-qwvg-p99c, RUSTSEC-2021-0078
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2021-07-07
Source: https://osv.dev/vulnerability/CVE-2021-32715
Type: osv

## Details
hyper is an HTTP library for rust. hyper's HTTP/1 server code had a flaw that incorrectly parses and accepts requests with a `Content-Length` header with a prefixed plus sign, when it should have been rejected as illegal. This combined with an upstream HTTP proxy that doesn't parse such `Content-Length` headers, but forwards them, can result in "request smuggling" or "desync attacks". The flaw exists in all prior versions of hyper prior to 0.14.10, if built with `rustc` v1.5.0 or newer. The vulnerability is patched in hyper version 0.14.10. Two workarounds exist: One may reject requests manually that contain a plus sign prefix in the `Content-Length` header or ensure any upstream proxy handles `Content-Length` headers with a plus sign prefix.

## References
- https://github.com/rust-lang/rust/pull/28826/commits/123a83326fb95366e94a3be1a74775df4db97739
- https://github.com/hyperium/hyper/security/advisories/GHSA-f3pg-qwvg-p99c
