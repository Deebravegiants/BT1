# [H] ALPINE-CVE-2022-27780

## Summary
Severity: High
Advisory: ALPINE-CVE-2022-27780
Ecosystem: Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2022-06-02
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-27780
Type: osv

## Affected
- Alpine:v3.15: `curl` — affected >=7.80.0 <7.80.0-r2
- Alpine:v3.16: `curl` — affected >=7.80.0 <7.83.1-r0
- Alpine:v3.17: `curl` — affected >=7.80.0 <7.83.1-r0
- Alpine:v3.18: `curl` — affected >=7.80.0 <7.83.1-r0
- Alpine:v3.19: `curl` — affected >=7.80.0 <7.83.1-r0
- Alpine:v3.20: `curl` — affected >=7.80.0 <7.83.1-r0
- Alpine:v3.21: `curl` — affected >=7.80.0 <7.83.1-r0
- Alpine:v3.22: `curl` — affected >=7.80.0 <7.83.1-r0
- Alpine:v3.23: `curl` — affected >=7.80.0 <7.83.1-r0
- Alpine:v3.24: `curl` — affected >=7.80.0 <7.83.1-r0

## Details
The curl URL parser wrongly accepts percent-encoded URL separators like '/'when decoding the host name part of a URL, making it a *different* URL usingthe wrong host name when it is later retrieved.For example, a URL like `http://example.com%2F127.0.0.1/`, would be allowed bythe parser and get transposed into `http://example.com/127.0.0.1/`. This flawcan be used to circumvent filters, checks and more.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-27780
