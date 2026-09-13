# [H] ALPINE-CVE-2023-34241

## Summary
Severity: High
Advisory: ALPINE-CVE-2023-34241
Ecosystem: Alpine:v3.15, Alpine:v3.16, Alpine:v3.17
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2023-06-22
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-34241
Type: osv

## Affected
- Alpine:v3.15: `cups` — affected >=2.2.0 <2.3.3-r8
- Alpine:v3.16: `cups` — affected >=2.2.0 <2.4.2-r2
- Alpine:v3.17: `cups` — affected >=2.2.0 <2.4.2-r3

## Details
OpenPrinting CUPS is a standards-based, open source printing system for Linux and other Unix-like operating systems. Starting in version 2.0.0 and prior to version 2.4.6, CUPS logs data of free memory to the logging service AFTER the connection has been closed, when it should have logged the data right before. This is a use-after-free bug that impacts the entire cupsd process.

The exact cause of this issue is the function `httpClose(con->http)` being called in `scheduler/client.c`. The problem is that httpClose always, provided its argument is not null, frees the pointer at the end of the call, only for cupsdLogClient to pass the pointer to httpGetHostname. This issue happens in function `cupsdAcceptClient` if LogLevel is warn or higher and in two scenarios: there is a double-lookup for the IP Address (HostNameLookups Double is set in `cupsd.conf`) which fails to resolve, or if CUPS is compiled with TCP wrappers and the connection is refused by rules from `/etc/hosts.allow` and `/etc/hosts.deny`.

Version 2.4.6 has a patch for this issue.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-34241
