# [M] ALPINE-CVE-2024-47081

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2024-47081
Ecosystem: Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.3 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2025-06-09
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-47081
Type: osv

## Affected
- Alpine:v3.19: `py3-requests` — affected >=0 <2.32.4-r0
- Alpine:v3.20: `py3-requests` — affected >=0 <2.32.4-r0
- Alpine:v3.21: `py3-requests` — affected >=0 <2.32.4-r0
- Alpine:v3.22: `py3-requests` — affected >=0 <2.32.4-r0
- Alpine:v3.23: `py3-requests` — affected >=0 <2.32.4-r0
- Alpine:v3.24: `py3-requests` — affected >=0 <2.32.4-r0

## Details
Requests is a HTTP library. Due to a URL parsing issue, Requests releases prior to 2.32.4 may leak .netrc credentials to third parties for specific maliciously-crafted URLs. Users should upgrade to version 2.32.4 to receive a fix. For older versions of Requests, use of the .netrc file can be disabled with `trust_env=False` on one's Requests Session.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-47081
