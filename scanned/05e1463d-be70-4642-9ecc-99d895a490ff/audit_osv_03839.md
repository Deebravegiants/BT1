# [H] ALPINE-CVE-2026-56018

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-56018
Ecosystem: Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-06-29
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-56018
Type: osv

## Affected
- Alpine:v3.24: `perl-javascript-minifier-xs` — affected >=0 <0.16-r0

## Details
JavaScript::Minifier::XS versions before 0.16 for Perl leak memory on every call to minify(), allowing unbounded memory growth.

In JsMinify (XS.xs) the cleanup frees only the NodeSet structures and never the per-token contents buffers allocated in JsSetNodeContents; JsDiscardNode unlinks nodes without freeing their contents. Each token's contents buffer is therefore leaked on every call, and the two early returns taken when the node list is empty leak the whole NodeSet.

A long-lived process that minifies repeatedly, such as an asset pipeline or a server-side minifier endpoint, grows in memory without bound until it exhausts available memory and is killed, causing denial of service.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-56018
