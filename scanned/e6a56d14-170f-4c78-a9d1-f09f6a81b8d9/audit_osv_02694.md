# [H] ALPINE-CVE-2022-42915

## Summary
Severity: High
Advisory: ALPINE-CVE-2022-42915
Ecosystem: Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-10-29
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-42915
Type: osv

## Affected
- Alpine:v3.15: `curl` — affected >=7.77.0 <7.80.0-r4
- Alpine:v3.16: `curl` — affected >=7.77.0 <7.83.1-r4
- Alpine:v3.17: `curl` — affected >=7.77.0 <7.86.0-r0
- Alpine:v3.18: `curl` — affected >=7.77.0 <7.86.0-r0
- Alpine:v3.19: `curl` — affected >=7.77.0 <7.86.0-r0
- Alpine:v3.20: `curl` — affected >=7.77.0 <7.86.0-r0
- Alpine:v3.21: `curl` — affected >=7.77.0 <7.86.0-r0
- Alpine:v3.22: `curl` — affected >=7.77.0 <7.86.0-r0
- Alpine:v3.23: `curl` — affected >=7.77.0 <7.86.0-r0
- Alpine:v3.24: `curl` — affected >=7.77.0 <7.86.0-r0

## Details
curl before 7.86.0 has a double free. If curl is told to use an HTTP proxy for a transfer with a non-HTTP(S) URL, it sets up the connection to the remote server by issuing a CONNECT request to the proxy, and then tunnels the rest of the protocol through. An HTTP proxy might refuse this request (HTTP proxies often only allow outgoing connections to specific port numbers, like 443 for HTTPS) and instead return a non-200 status code to the client. Due to flaws in the error/cleanup handling, this could trigger a double free in curl if one of the following schemes were used in the URL for the transfer: dict, gopher, gophers, ldap, ldaps, rtmp, rtmps, or telnet. The earliest affected version is 7.77.0.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-42915
