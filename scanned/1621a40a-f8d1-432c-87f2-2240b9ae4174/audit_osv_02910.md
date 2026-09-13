# [H] ALPINE-CVE-2023-46848

## Summary
Severity: High
Advisory: ALPINE-CVE-2023-46848
Ecosystem: Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-11-03
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-46848
Type: osv

## Affected
- Alpine:v3.19: `squid` — affected >=5.0.3 <6.4-r0
- Alpine:v3.20: `squid` — affected >=5.0.3 <6.4-r0
- Alpine:v3.21: `squid` — affected >=5.0.3 <6.4-r0
- Alpine:v3.22: `squid` — affected >=5.0.3 <6.4-r0
- Alpine:v3.23: `squid` — affected >=5.0.3 <6.4-r0
- Alpine:v3.24: `squid` — affected >=5.0.3 <6.4-r0

## Details
Squid is vulnerable to Denial of Service,  where a remote attacker can perform DoS by sending ftp:// URLs in HTTP Request messages or constructing ftp:// URLs from FTP Native input.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-46848
