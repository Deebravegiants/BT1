# [H] ALPINE-CVE-2023-49288

## Summary
Severity: High
Advisory: ALPINE-CVE-2023-49288
Ecosystem: Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-12-04
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-49288
Type: osv

## Affected
- Alpine:v3.19: `squid` — affected >=3.5 <6.1-r0
- Alpine:v3.20: `squid` — affected >=3.5 <6.1-r0
- Alpine:v3.21: `squid` — affected >=3.5 <6.1-r0
- Alpine:v3.22: `squid` — affected >=3.5 <6.1-r0
- Alpine:v3.23: `squid` — affected >=3.5 <6.1-r0
- Alpine:v3.24: `squid` — affected >=3.5 <6.1-r0

## Details
Squid is a caching proxy for the Web supporting HTTP, HTTPS, FTP, and more. Affected versions of squid are subject to a a Use-After-Free bug which can lead to a Denial of Service attack via collapsed forwarding. All versions of Squid from 3.5 up to and including 5.9 configured with "collapsed_forwarding on" are vulnerable. Configurations with "collapsed_forwarding off" or without a "collapsed_forwarding" directive are not vulnerable. This bug is fixed by Squid version 6.0.1. Users are advised to upgrade. Users unable to upgrade should remove all collapsed_forwarding lines from their squid.conf.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-49288
