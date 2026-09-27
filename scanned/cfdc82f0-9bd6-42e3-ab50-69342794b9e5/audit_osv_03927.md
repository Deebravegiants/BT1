# [H] ALPINE-CVE-2026-6732

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-6732
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-04-23
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-6732
Type: osv

## Affected
- Alpine:v3.21: `libxml2` — affected >=2.13.0 <2.13.9-r1
- Alpine:v3.22: `libxml2` — affected >=2.13.0 <2.13.9-r1
- Alpine:v3.23: `libxml2` — affected >=2.13.0 <2.13.9-r1
- Alpine:v3.24: `libxml2` — affected >=2.13.0 <2.13.9-r2

## Details
A flaw was found in libxml2. This vulnerability occurs when the library processes a specially crafted XML Schema Definition (XSD) validated document that includes an internal entity reference. An attacker could exploit this by providing a malicious document, leading to a type confusion error that causes the application to crash. This results in a denial of service (DoS), making the affected system or application unavailable.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-6732
