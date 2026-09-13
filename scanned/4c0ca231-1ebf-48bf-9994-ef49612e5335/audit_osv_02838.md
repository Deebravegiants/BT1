# [M] ALPINE-CVE-2023-34323

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2023-34323
Ecosystem: Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-01-05
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-34323
Type: osv

## Affected
- Alpine:v3.15: `xen` — affected >=0 <4.15.5-r3
- Alpine:v3.16: `xen` — affected >=0 <4.16.5-r3
- Alpine:v3.17: `xen` — affected >=0 <4.16.5-r3
- Alpine:v3.18: `xen` — affected >=0 <4.17.2-r3
- Alpine:v3.19: `xen` — affected >=0 <4.17.2-r3
- Alpine:v3.20: `xen` — affected >=0 <4.17.2-r3
- Alpine:v3.21: `xen` — affected >=0 <4.17.2-r3
- Alpine:v3.22: `xen` — affected >=0 <4.17.2-r3
- Alpine:v3.23: `xen` — affected >=0 <4.17.2-r3
- Alpine:v3.24: `xen` — affected >=0 <4.17.2-r3

## Details
When a transaction is committed, C Xenstored will first check
the quota is correct before attempting to commit any nodes.  It would
be possible that accounting is temporarily negative if a node has
been removed outside of the transaction.

Unfortunately, some versions of C Xenstored are assuming that the
quota cannot be negative and are using assert() to confirm it.  This
will lead to C Xenstored crash when tools are built without -DNDEBUG
(this is the default).

## References
- https://security.alpinelinux.org/vuln/CVE-2023-34323
