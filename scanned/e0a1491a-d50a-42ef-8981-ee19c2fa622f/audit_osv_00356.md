# [M] ALPINE-CVE-2017-1000101

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2017-1000101
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.3, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2017-10-05
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-1000101
Type: osv

## Affected
- Alpine:v3.10: `curl` — affected >=0 <7.55.0-r0
- Alpine:v3.11: `curl` — affected >=0 <7.55.0-r0
- Alpine:v3.12: `curl` — affected >=0 <7.55.0-r0
- Alpine:v3.13: `curl` — affected >=0 <7.55.0-r0
- Alpine:v3.14: `curl` — affected >=0 <7.55.0-r0
- Alpine:v3.15: `curl` — affected >=0 <7.55.0-r0
- Alpine:v3.16: `curl` — affected >=0 <7.55.0-r0
- Alpine:v3.17: `curl` — affected >=0 <7.55.0-r0
- Alpine:v3.18: `curl` — affected >=0 <7.55.0-r0
- Alpine:v3.19: `curl` — affected >=0 <7.55.0-r0
- Alpine:v3.20: `curl` — affected >=0 <7.55.0-r0
- Alpine:v3.21: `curl` — affected >=0 <7.55.0-r0
- Alpine:v3.22: `curl` — affected >=0 <7.55.0-r0
- Alpine:v3.23: `curl` — affected >=0 <7.55.0-r0
- Alpine:v3.24: `curl` — affected >=0 <7.55.0-r0
- Alpine:v3.3: `curl` — affected >=0 <7.55.0-r0
- Alpine:v3.4: `curl` — affected >=0 <7.55.0-r0
- Alpine:v3.5: `curl` — affected >=0 <7.55.0-r0
- Alpine:v3.6: `curl` — affected >=0 <7.55.0-r0
- Alpine:v3.7: `curl` — affected >=0 <7.55.0-r0
- Alpine:v3.8: `curl` — affected >=0 <7.55.0-r0
- Alpine:v3.9: `curl` — affected >=0 <7.55.0-r0

## Details
curl supports "globbing" of URLs, in which a user can pass a numerical range to have the tool iterate over those numbers to do a sequence of transfers. In the globbing function that parses the numerical range, there was an omission that made curl read a byte beyond the end of the URL if given a carefully crafted, or just wrongly written, URL. The URL is stored in a heap based buffer, so it could then be made to wrongly read something else instead of crashing. An example of a URL that triggers the flaw would be `http://ur%20[0-60000000000000000000`.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-1000101
