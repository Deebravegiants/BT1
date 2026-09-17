# [H] ALPINE-CVE-2022-1473

## Summary
Severity: High
Advisory: ALPINE-CVE-2022-1473
Ecosystem: Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-05-03
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-1473
Type: osv

## Affected
- Alpine:v3.17: `openssl` — affected >=3.0.0 <3.0.3-r0
- Alpine:v3.18: `openssl` — affected >=3.0.0 <3.0.3-r0
- Alpine:v3.19: `openssl` — affected >=3.0.0 <3.0.3-r0
- Alpine:v3.20: `openssl` — affected >=3.0.0 <3.0.3-r0
- Alpine:v3.21: `openssl` — affected >=3.0.0 <3.0.3-r0
- Alpine:v3.22: `openssl` — affected >=3.0.0 <3.0.3-r0
- Alpine:v3.23: `openssl` — affected >=3.0.0 <3.0.3-r0
- Alpine:v3.24: `openssl` — affected >=3.0.0 <3.0.3-r0
- Alpine:v3.15: `openssl3` — affected >=0 <3.0.3-r0
- Alpine:v3.16: `openssl3` — affected >=0 <3.0.3-r0

## Details
The OPENSSL_LH_flush() function, which empties a hash table, contains a bug that breaks reuse of the memory occuppied by the removed hash table entries. This function is used when decoding certificates or keys. If a long lived process periodically decodes certificates or keys its memory usage will expand without bounds and the process might be terminated by the operating system causing a denial of service. Also traversing the empty hash table entries will take increasingly more time. Typically such long lived processes might be TLS clients or TLS servers configured to accept client certificate authentication. The function was added in the OpenSSL 3.0 version thus older releases are not affected by the issue. Fixed in OpenSSL 3.0.3 (Affected 3.0.0,3.0.1,3.0.2).

## References
- https://security.alpinelinux.org/vuln/CVE-2022-1473
