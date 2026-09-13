# [M] HTTP Request Smuggling in hyper

## Summary
Severity: Medium
Advisory: GHSA-6hfq-h8hq-87mf
CVE: CVE-2021-21299
CWE: CWE-444
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-6hfq-h8hq-87mf
Type: github-advisory

## Affected
- crates.io: `hyper` — affected >=0.14.0 <0.14.3
- crates.io: `hyper` — affected >=0.13.0 <0.13.10
- crates.io: `hyper` — affected >=0.12.0 <0.12.36

## Details
### Summary

hyper's HTTP server code had a flaw that incorrectly understands some requests with multiple transfer-encoding headers to have a chunked payload, when it should have been rejected as illegal. This combined with an upstream HTTP proxy that understands the request payload boundary differently can result in "request smuggling" or "desync attacks".

### Vulnerability

The flaw was introduced in https://github.com/hyperium/hyper/commit/26417fc24a7d05df538e0f39239b373c5c3d61f6, released in v0.12.0.

Consider this example request:

```
POST /yolo HTTP/1.1
Transfer-Encoding: chunked
Transfer-Encoding: cow
```

This request *should* be rejected, according to RFC 7230, since it has a `Transfer-Encoding` header, but after folding, it does not end in `chunked`. hyper would notice the `chunked` in the first line, and then check the second line, and thanks to a missing boolean assignment, *not* set the error condition. hyper would treat the payload as being `chunked`. By differing from the spec, it is possible to send requests like these to endpoints that have different HTTP implementations, with different interpretations of the payload semantics, and cause "desync attacks".

There are several parts of the spec that must also be checked, and hyper correctly handles all of those. Additionally, hyper's *client* does not allow sending requests with improper headers, so the misunderstanding cannot be propagated further.

Read more about desync attacks: https://portswigger.net/research/http-desync-attacks-request-smuggling-reborn

### Impact

To determine if vulnerable, all these things must be true:

- **Using hyper as an HTTP *server*.** The client is not affected.
- **Using HTTP/1.1.** HTTP/2 does not use `transfer-encoding`.
- **Using a vulnerable HTTP proxy upstream to hyper.** If an upstream proxy correctly rejects the illegal transfer-encoding headers, the desync attack cannot succeed. If there is *no* proxy upstream of hyper, hyper cannot *start* the desync attack, as the client will repair the headers before forwarding.

### Patches

We have released and backported the following patch versions:

- v0.14.3
- v0.13.10

### Workarounds

Besides upgrading hyper, you can take the following options:

- Reject requests that contain a `transfer-encoding` header.
- Ensure any upstream proxy handles `transfer-encoding` correctly.

### Credits

This issue was initially reported by ZeddYu Lu From Qi An Xin Technology Research Institute.

## References
- https://github.com/hyperium/hyper/security/advisories/GHSA-6hfq-h8hq-87mf
- https://nvd.nist.gov/vuln/detail/CVE-2021-21299
- https://github.com/hyperium/hyper/commit/8f93123efef5c1361086688fe4f34c83c89cec02
- https://github.com/hyperium/hyper
- https://portswigger.net/research/http-desync-attacks-request-smuggling-reborn
- https://rustsec.org/advisories/RUSTSEC-2021-0020.html
