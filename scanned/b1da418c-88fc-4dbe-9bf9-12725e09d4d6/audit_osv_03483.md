# [C] ALPINE-CVE-2026-19931

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2026-19931
Ecosystem: Alpine:v3.23, Alpine:v3.24
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-09-06
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-19931
Type: osv

## Affected
- Alpine:v3.23: `curl` — affected >=0 <8.22.0-r0
- Alpine:v3.24: `curl` — affected >=0 <8.22.0-r0

## Details
A flaw in libcurl makes it wrongly reuse an HTTP connection setup for a given
hostname using Negotiate authentication, when the initial request is done
using empty credentials. This can make user B's request get sent over user A's
previously authenticated connection.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-19931
