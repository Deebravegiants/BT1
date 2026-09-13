# [H] ALPINE-CVE-2024-24806

## Summary
Severity: High
Advisory: ALPINE-CVE-2024-24806
Ecosystem: Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2024-02-07
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-24806
Type: osv

## Affected
- Alpine:v3.20: `libuv` — affected >=1.24.0 <1.48.0-r0
- Alpine:v3.21: `libuv` — affected >=1.24.0 <1.48.0-r0
- Alpine:v3.22: `libuv` — affected >=1.24.0 <1.48.0-r0
- Alpine:v3.23: `libuv` — affected >=1.24.0 <1.48.0-r0
- Alpine:v3.24: `libuv` — affected >=1.24.0 <1.48.0-r0

## Details
libuv is a multi-platform support library with a focus on asynchronous I/O. The `uv_getaddrinfo` function in `src/unix/getaddrinfo.c` (and its windows counterpart `src/win/getaddrinfo.c`), truncates hostnames to 256 characters before calling `getaddrinfo`. This behavior can be exploited to create addresses like `0x00007f000001`, which are considered valid by `getaddrinfo` and could allow an attacker to craft payloads that resolve to unintended IP addresses, bypassing developer checks. The vulnerability arises due to how the `hostname_ascii` variable (with a length of 256 bytes) is handled in `uv_getaddrinfo` and subsequently in `uv__idna_toascii`. When the hostname exceeds 256 characters, it gets truncated without a terminating null byte. As a result attackers may be able to access internal APIs or for websites (similar to MySpace) that allows users to have `username.example.com` pages. Internal services that crawl or cache these user pages can be exposed to SSRF attacks if a malicious user chooses a long vulnerable username. This issue has been addressed in release version 1.48.0. Users are advised to upgrade. There are no known workarounds for this vulnerability.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-24806
