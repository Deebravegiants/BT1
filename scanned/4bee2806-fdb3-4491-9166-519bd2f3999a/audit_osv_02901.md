# [H] ALPINE-CVE-2023-46724

## Summary
Severity: High
Advisory: ALPINE-CVE-2023-46724
Ecosystem: Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-11-01
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-46724
Type: osv

## Affected
- Alpine:v3.19: `squid` — affected >=3.3.0.1 <6.4-r0
- Alpine:v3.20: `squid` — affected >=3.3.0.1 <6.4-r0
- Alpine:v3.21: `squid` — affected >=3.3.0.1 <6.4-r0
- Alpine:v3.22: `squid` — affected >=3.3.0.1 <6.4-r0
- Alpine:v3.23: `squid` — affected >=3.3.0.1 <6.4-r0
- Alpine:v3.24: `squid` — affected >=3.3.0.1 <6.4-r0

## Details
Squid is a caching proxy for the Web. Due to an Improper Validation of Specified Index bug, Squid versions 3.3.0.1 through 5.9 and 6.0 prior to 6.4 compiled using `--with-openssl` are vulnerable to a Denial of Service attack against SSL Certificate validation. This problem allows a remote server to perform Denial of Service against Squid Proxy by initiating a TLS Handshake with a specially crafted SSL Certificate in a server certificate chain. This attack is limited to HTTPS and SSL-Bump. This bug is fixed in Squid version 6.4. In addition, patches addressing this problem for the stable releases can be found in Squid's patch archives. Those who you use a prepackaged version of Squid should refer to the package vendor for availability information on updated packages.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-46724
