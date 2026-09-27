# [M] ALPINE-CVE-2026-3783

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-3783
Ecosystem: Alpine:v3.23, Alpine:v3.24
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-03-11
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-3783
Type: osv

## Affected
- Alpine:v3.23: `curl` — affected >=7.33.0 <8.19.0-r0
- Alpine:v3.24: `curl` — affected >=7.33.0 <8.19.0-r0

## Details
When an OAuth2 bearer token is used for an HTTP(S) transfer, and that transfer
performs a redirect to a second URL, curl could leak that token to the second
hostname under some circumstances.

If the hostname that the first request is redirected to has information in the
used .netrc file, with either of the `machine` or `default` keywords, curl
would pass on the bearer token set for the first host also to the second one.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-3783
