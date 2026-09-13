# [H] ALPINE-CVE-2026-56017

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-56017
Ecosystem: Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-06-29
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-56017
Type: osv

## Affected
- Alpine:v3.24: `perl-javascript-minifier-xs` — affected >=0 <0.16-r0

## Details
JavaScript::Minifier::XS versions before 0.16 for Perl crash with a NULL pointer dereference when the first meaningful token of the input is a slash.

The regexp versus division disambiguator in JsTokenizeString (XS.xs) inspects the previous token's last byte to choose between a regexp literal and a division operator. When a slash is the first meaningful token, with the start of input or only whitespace and comments before it, there is no valid preceding token: the walk back over whitespace and comment nodes runs off the head of the node list to NULL, and the byte lookup reads through a NULL contents pointer at an underflowed length index. The following identifier check dereferences the same NULL pointer.

The crash is reachable through the public minify() API, so input as small as a single slash byte crashes the calling process. A service that minifies untrusted or third-party JavaScript can be crashed by a remote request, causing denial of service.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-56017
