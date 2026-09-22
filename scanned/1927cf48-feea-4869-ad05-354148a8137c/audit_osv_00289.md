# [M] ALPINE-CVE-2016-9318

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2016-9318
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.2, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.3, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2016-11-16
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-9318
Type: osv

## Affected
- Alpine:v3.10: `libxml2` — affected >=0 <2.9.4-r2
- Alpine:v3.11: `libxml2` — affected >=0 <2.9.4-r2
- Alpine:v3.12: `libxml2` — affected >=0 <2.9.4-r2
- Alpine:v3.13: `libxml2` — affected >=0 <2.9.4-r2
- Alpine:v3.14: `libxml2` — affected >=0 <2.9.4-r2
- Alpine:v3.15: `libxml2` — affected >=0 <2.9.4-r2
- Alpine:v3.16: `libxml2` — affected >=0 <2.9.4-r2
- Alpine:v3.17: `libxml2` — affected >=0 <2.9.4-r2
- Alpine:v3.18: `libxml2` — affected >=0 <2.9.4-r2
- Alpine:v3.19: `libxml2` — affected >=0 <2.9.4-r2
- Alpine:v3.2: `libxml2` — affected >=0 <2.9.4-r2
- Alpine:v3.20: `libxml2` — affected >=0 <2.9.4-r2
- Alpine:v3.21: `libxml2` — affected >=0 <2.9.4-r2
- Alpine:v3.22: `libxml2` — affected >=0 <2.9.4-r2
- Alpine:v3.23: `libxml2` — affected >=0 <2.9.4-r2
- Alpine:v3.24: `libxml2` — affected >=0 <2.9.4-r2
- Alpine:v3.3: `libxml2` — affected >=0 <2.9.4-r2
- Alpine:v3.4: `libxml2` — affected >=0 <2.9.4-r2
- Alpine:v3.5: `libxml2` — affected >=0 <2.9.4-r2
- Alpine:v3.6: `libxml2` — affected >=0 <2.9.4-r2
- Alpine:v3.7: `libxml2` — affected >=0 <2.9.4-r2
- Alpine:v3.8: `libxml2` — affected >=0 <2.9.4-r2
- Alpine:v3.9: `libxml2` — affected >=0 <2.9.4-r2

## Details
libxml2 2.9.4 and earlier, as used in XMLSec 1.2.23 and earlier and other products, does not offer a flag directly indicating that the current document may be read but other files may not be opened, which makes it easier for remote attackers to conduct XML External Entity (XXE) attacks via a crafted document.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-9318
