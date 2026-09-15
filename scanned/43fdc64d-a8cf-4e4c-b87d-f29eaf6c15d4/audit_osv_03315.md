# [C] ALPINE-CVE-2025-49794

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2025-49794
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H)
Published: 2025-06-16
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-49794
Type: osv

## Affected
- Alpine:v3.21: `libxml2` — affected >=0 <2.13.9-r0
- Alpine:v3.22: `libxml2` — affected >=0 <2.13.9-r0
- Alpine:v3.23: `libxml2` — affected >=0 <2.13.9-r0
- Alpine:v3.24: `libxml2` — affected >=0 <2.13.9-r0

## Details
A use-after-free vulnerability was found in libxml2. This issue occurs when parsing XPath elements under certain circumstances when the XML schematron has the <sch:name path="..."/> schema elements. This flaw allows a malicious actor to craft a malicious XML document used as input for libxml, resulting in the program's crash using libxml or other possible undefined behaviors.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-49794
