# [H] conduit-hyper vulnerable to Denial of Service from unchecked request length

## Summary
Severity: High
Advisory: GHSA-9398-5ghf-7pr6
CVE: CVE-2022-39294
CWE: CWE-1284, CWE-400
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-10-31
Source: https://github.com/advisories/GHSA-9398-5ghf-7pr6
Type: github-advisory

## Affected
- crates.io: `conduit-hyper` — affected >=0.2.0-alpha.3 <0.4.2

## Details
Prior to version 0.4.2, `conduit-hyper` did not check any limit on a request's length before calling [`hyper::body::to_bytes`](https://docs.rs/hyper/latest/hyper/body/fn.to_bytes.html). An attacker could send a malicious request with an abnormally large `Content-Length`, which could lead to a panic if memory allocation failed for that request.

In version 0.4.2, `conduit-hyper` sets an internal limit of 128 MiB per request, otherwise returning status 400 ("Bad Request").

This crate is part of the implementation of Rust's [crates.io](https://crates.io/), but that service is not affected due to its existing cloud infrastructure, which already drops such malicious requests. Even with the new limit in place, `conduit-hyper` is not recommended for production use, nor to directly serve the public Internet.

The vulnerability was discovered by Ori Hollander from the JFrog Security Research team.

## References
- https://github.com/conduit-rust/conduit-hyper/security/advisories/GHSA-9398-5ghf-7pr6
- https://nvd.nist.gov/vuln/detail/CVE-2022-39294
- https://github.com/conduit-rust/conduit-hyper/commit/4d225a53206505d39438ec6694e15f49c038baff
- https://github.com/conduit-rust/conduit-hyper
- https://rustsec.org/advisories/RUSTSEC-2022-0066.html
