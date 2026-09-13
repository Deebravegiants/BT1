# [M] ALPINE-CVE-2022-27779

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2022-27779
Ecosystem: Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2022-06-02
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-27779
Type: osv

## Affected
- Alpine:v3.16: `curl` — affected >=7.82.0 <7.83.1-r0
- Alpine:v3.17: `curl` — affected >=7.82.0 <7.83.1-r0
- Alpine:v3.18: `curl` — affected >=7.82.0 <7.83.1-r0
- Alpine:v3.19: `curl` — affected >=7.82.0 <7.83.1-r0
- Alpine:v3.20: `curl` — affected >=7.82.0 <7.83.1-r0
- Alpine:v3.21: `curl` — affected >=7.82.0 <7.83.1-r0
- Alpine:v3.22: `curl` — affected >=7.82.0 <7.83.1-r0
- Alpine:v3.23: `curl` — affected >=7.82.0 <7.83.1-r0
- Alpine:v3.24: `curl` — affected >=7.82.0 <7.83.1-r0

## Details
libcurl wrongly allows cookies to be set for Top Level Domains (TLDs) if thehost name is provided with a trailing dot.curl can be told to receive and send cookies. curl's "cookie engine" can bebuilt with or without [Public Suffix List](https://publicsuffix.org/)awareness. If PSL support not provided, a more rudimentary check exists to atleast prevent cookies from being set on TLDs. This check was broken if thehost name in the URL uses a trailing dot.This can allow arbitrary sites to set cookies that then would get sent to adifferent and unrelated site or domain.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-27779
