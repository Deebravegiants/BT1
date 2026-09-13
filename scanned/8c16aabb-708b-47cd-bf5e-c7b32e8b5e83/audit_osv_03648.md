# [M] ALPINE-CVE-2026-39316

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-39316
Ecosystem: Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.2 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-04-07
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-39316
Type: osv

## Affected
- Alpine:v3.20: `cups` — affected >=0 <2.4.18-r0
- Alpine:v3.21: `cups` — affected >=0 <2.4.18-r0
- Alpine:v3.22: `cups` — affected >=0 <2.4.18-r0
- Alpine:v3.23: `cups` — affected >=0 <2.4.18-r0
- Alpine:v3.24: `cups` — affected >=0 <2.4.18-r0

## Details
OpenPrinting CUPS is an open source printing system for Linux and other Unix-like operating systems. In versions 2.4.16 and prior, a use-after-free vulnerability exists in the CUPS scheduler (cupsd) when temporary printers are automatically deleted. cupsdDeleteTemporaryPrinters() in scheduler/printers.c calls cupsdDeletePrinter() without first expiring subscriptions that reference the printer, leaving cupsd_subscription_t.dest as a dangling pointer to freed heap memory. The dangling pointer is subsequently dereferenced at multiple code sites, causing a crash (denial of service) of the cupsd daemon. With heap grooming, this can be leveraged for code execution.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-39316
