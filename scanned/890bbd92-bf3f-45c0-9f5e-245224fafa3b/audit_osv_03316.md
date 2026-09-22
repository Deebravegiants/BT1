# [H] ALPINE-CVE-2025-49795

## Summary
Severity: High
Advisory: ALPINE-CVE-2025-49795
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-06-16
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-49795
Type: osv

## Affected
- Alpine:v3.21: `libxml2` — affected >=0 <2.13.9-r0
- Alpine:v3.22: `libxml2` — affected >=0 <2.13.9-r0
- Alpine:v3.23: `libxml2` — affected >=0 <2.13.9-r0
- Alpine:v3.24: `libxml2` — affected >=0 <2.13.9-r0

## Details
A NULL pointer dereference vulnerability was found in libxml2 when processing XPath XML expressions. This flaw allows an attacker to craft a malicious XML input to libxml2, leading to a denial of service.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-49795
