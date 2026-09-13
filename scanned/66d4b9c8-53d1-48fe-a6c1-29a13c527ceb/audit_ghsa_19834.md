# [M] Web Push Denial of Service via malicious Web Push endpoint

## Summary
Severity: Medium
Advisory: GHSA-fc83-9jwq-gc2m
CWE: CWE-770
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-03-24
Source: https://github.com/advisories/GHSA-fc83-9jwq-gc2m
Type: github-advisory

## Affected
- crates.io: `web-push` — affected >=0 <0.10.4

## Details
Prior to version 0.10.3, the built-in clients of the `web-push` crate eagerly allocated memory based on the `Content-Length` header returned by the Web Push endpoint. Malicious Web Push endpoints could return a large `Content-Length` without ever having to send as much data, leading to denial of service by memory exhaustion.

Services providing Web Push notifications typically allow the user to register an arbitrary endpoint, so the endpoint should not be trusted.

The fixed version 0.10.3 now limits the amount of memory it will allocate for each response, limits the amount of data it will read from the endpoint, and returns an error if the endpoint sends too much data.

As before, it is recommended that services add a timeout for each request to Web Push endpoints.

## References
- https://github.com/pimeys/rust-web-push/pull/68
- https://github.com/pimeys/rust-web-push
- https://rustsec.org/advisories/RUSTSEC-2025-0015.html
