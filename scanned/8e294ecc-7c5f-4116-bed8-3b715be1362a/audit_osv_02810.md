# [M] ALPINE-CVE-2023-28321

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2023-28321
Ecosystem: Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2023-05-26
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-28321
Type: osv

## Affected
- Alpine:v3.15: `curl` — affected >=0 <8.1.0-r0
- Alpine:v3.16: `curl` — affected >=0 <8.1.0-r0
- Alpine:v3.17: `curl` — affected >=0 <8.1.0-r0
- Alpine:v3.18: `curl` — affected >=0 <8.1.0-r0
- Alpine:v3.19: `curl` — affected >=0 <8.1.0-r0
- Alpine:v3.20: `curl` — affected >=0 <8.1.0-r0
- Alpine:v3.21: `curl` — affected >=0 <8.1.0-r0
- Alpine:v3.22: `curl` — affected >=0 <8.1.0-r0
- Alpine:v3.23: `curl` — affected >=0 <8.1.0-r0
- Alpine:v3.24: `curl` — affected >=0 <8.1.0-r0

## Details
An improper certificate validation vulnerability exists in curl <v8.1.0 in the way it supports matching of wildcard patterns when listed as "Subject Alternative Name" in TLS server certificates. curl can be built to use its own name matching function for TLS rather than one provided by a TLS library. This private wildcard matching function would match IDN (International Domain Name) hosts incorrectly and could as a result accept patterns that otherwise should mismatch. IDN hostnames are converted to puny code before used for certificate checks. Puny coded names always start with `xn--` and should not be allowed to pattern match, but the wildcard check in curl could still check for `x*`, which would match even though the IDN name most likely contained nothing even resembling an `x`.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-28321
