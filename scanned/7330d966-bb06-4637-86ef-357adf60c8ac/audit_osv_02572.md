# [M] ALPINE-CVE-2022-32205

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2022-32205
Ecosystem: Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:L)
Published: 2022-07-07
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-32205
Type: osv

## Affected
- Alpine:v3.13: `curl` — affected >=7.71.0 <7.79.1-r2
- Alpine:v3.14: `curl` — affected >=7.71.0 <7.79.1-r2
- Alpine:v3.15: `curl` — affected >=7.71.0 <7.80.0-r2
- Alpine:v3.16: `curl` — affected >=7.71.0 <7.83.1-r2
- Alpine:v3.17: `curl` — affected >=7.71.0 <7.84.0-r0
- Alpine:v3.18: `curl` — affected >=7.71.0 <7.84.0-r0
- Alpine:v3.19: `curl` — affected >=7.71.0 <7.84.0-r0
- Alpine:v3.20: `curl` — affected >=7.71.0 <7.84.0-r0
- Alpine:v3.21: `curl` — affected >=7.71.0 <7.84.0-r0
- Alpine:v3.22: `curl` — affected >=7.71.0 <7.84.0-r0
- Alpine:v3.23: `curl` — affected >=7.71.0 <7.84.0-r0
- Alpine:v3.24: `curl` — affected >=7.71.0 <7.84.0-r0

## Details
A malicious server can serve excessive amounts of `Set-Cookie:` headers in a HTTP response to curl and curl < 7.84.0 stores all of them. A sufficiently large amount of (big) cookies make subsequent HTTP requests to this, or other servers to which the cookies match, create requests that become larger than the threshold that curl uses internally to avoid sending crazy large requests (1048576 bytes) and instead returns an error.This denial state might remain for as long as the same cookies are kept, match and haven't expired. Due to cookie matching rules, a server on `foo.example.com` can set cookies that also would match for `bar.example.com`, making it it possible for a "sister server" to effectively cause a denial of service for a sibling site on the same second level domain using this method.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-32205
