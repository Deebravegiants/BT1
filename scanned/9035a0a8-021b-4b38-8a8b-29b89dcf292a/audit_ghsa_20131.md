# [M] hyper-staticfile's location header incorporates user input, allowing open redirect

## Summary
Severity: Medium
Advisory: GHSA-5wvv-q5fv-2388
CWE: CWE-601
Ecosystem: crates.io
Published: 2022-12-30
Source: https://github.com/advisories/GHSA-5wvv-q5fv-2388
Type: github-advisory

## Affected
- crates.io: `hyper-staticfile` — affected >=0 <0.9.4
- crates.io: `hyper-staticfile` — affected >=0.10.0-alpha.1 <0.10.0-alpha.5

## Details
When `hyper-staticfile` performs a redirect for a directory request (e.g. a request for `/dir` that redirects to `/dir/`), the `Location` header value was derived from user input (the request path), simply appending a slash. The intent was to perform an origin-relative redirect, but specific inputs allowed performing a scheme-relative redirect instead.

An attacker could craft a special URL that would appear to be for the correct domain, but immediately redirects to a malicious domain. Such a URL can benefit phishing attacks, for example an innocent looking link in an email.

## References
- https://github.com/stephank/hyper-staticfile/commit/4db4afb811c553bc3d54a01a9985b9e6dfc5a115
- https://github.com/stephank/hyper-staticfile/commit/f12cadc6666c6f555d29725f5bc45da2103f24ea
- https://github.com/stephank/hyper-staticfile
- https://rustsec.org/advisories/RUSTSEC-2022-0072.html
