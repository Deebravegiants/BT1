# [H] ALPINE-CVE-2023-32233

## Summary
Severity: High
Advisory: ALPINE-CVE-2023-32233
Ecosystem: Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-05-08
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-32233
Type: osv

## Affected
- Alpine:v3.18: `linux-lts` — affected >=0 <6.1.27-r3
- Alpine:v3.19: `linux-lts` — affected >=0 <6.1.27-r3
- Alpine:v3.20: `linux-lts` — affected >=0 <6.1.27-r3
- Alpine:v3.21: `linux-lts` — affected >=0 <6.1.27-r3
- Alpine:v3.22: `linux-lts` — affected >=0 <6.1.27-r3
- Alpine:v3.23: `linux-lts` — affected >=0 <6.1.27-r3
- Alpine:v3.24: `linux-lts` — affected >=0 <6.1.27-r3

## Details
In the Linux kernel through 6.3.1, a use-after-free in Netfilter nf_tables when processing batch requests can be abused to perform arbitrary read and write operations on kernel memory. Unprivileged local users can obtain root privileges. This occurs because anonymous sets are mishandled.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-32233
