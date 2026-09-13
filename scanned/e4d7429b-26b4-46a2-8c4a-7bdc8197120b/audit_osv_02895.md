# [M] ALPINE-CVE-2023-45802

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2023-45802
Ecosystem: Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-10-23
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-45802
Type: osv

## Affected
- Alpine:v3.15: `apache2` — affected >=0 <2.4.58-r0
- Alpine:v3.16: `apache2` — affected >=0 <2.4.58-r0
- Alpine:v3.17: `apache2` — affected >=0 <2.4.58-r0
- Alpine:v3.18: `apache2` — affected >=0 <2.4.58-r0
- Alpine:v3.19: `apache2` — affected >=0 <2.4.58-r0
- Alpine:v3.20: `apache2` — affected >=0 <2.4.58-r0
- Alpine:v3.21: `apache2` — affected >=0 <2.4.58-r0
- Alpine:v3.22: `apache2` — affected >=0 <2.4.58-r0
- Alpine:v3.23: `apache2` — affected >=0 <2.4.58-r0
- Alpine:v3.24: `apache2` — affected >=0 <2.4.58-r0

## Details
When a HTTP/2 stream was reset (RST frame) by a client, there was a time window were the request's memory resources were not reclaimed immediately. Instead, de-allocation was deferred to connection close. A client could send new requests and resets, keeping the connection busy and open and causing the memory footprint to keep on growing. On connection close, all resources were reclaimed, but the process might run out of memory before that.

This was found by the reporter during testing of CVE-2023-44487 (HTTP/2 Rapid Reset Exploit) with their own test client. During "normal" HTTP/2 use, the probability to hit this bug is very low. The kept memory would not become noticeable before the connection closes or times out.

Users are recommended to upgrade to version 2.4.58, which fixes the issue.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-45802
