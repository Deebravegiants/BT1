# [H] ALPINE-CVE-2023-6516

## Summary
Severity: High
Advisory: ALPINE-CVE-2023-6516
Ecosystem: Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-02-13
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-6516
Type: osv

## Affected
- Alpine:v3.16: `bind` — affected >=9.16.0 <9.16.48-r0
- Alpine:v3.17: `bind` — affected >=9.16.0 <9.18.24-r0
- Alpine:v3.18: `bind` — affected >=9.16.0 <9.18.24-r0
- Alpine:v3.19: `bind` — affected >=9.16.0 <9.18.24-r0
- Alpine:v3.20: `bind` — affected >=9.16.0 <9.18.24-r0
- Alpine:v3.21: `bind` — affected >=9.16.0 <9.18.24-r0
- Alpine:v3.22: `bind` — affected >=9.16.0 <9.18.24-r0
- Alpine:v3.23: `bind` — affected >=9.16.0 <9.18.24-r0
- Alpine:v3.24: `bind` — affected >=9.16.0 <9.18.24-r0

## Details
To keep its cache database efficient, `named` running as a recursive resolver occasionally attempts to clean up the database. It uses several methods, including some that are asynchronous: a small chunk of memory pointing to the cache element that can be cleaned up is first allocated and then queued for later processing. It was discovered that if the resolver is continuously processing query patterns triggering this type of cache-database maintenance, `named` may not be able to handle the cleanup events in a timely manner. This in turn enables the list of queued cleanup events to grow infinitely large over time, allowing the configured `max-cache-size` limit to be significantly exceeded.
This issue affects BIND 9 versions 9.16.0 through 9.16.45 and 9.16.8-S1 through 9.16.45-S1.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-6516
