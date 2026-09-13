# [H] ALPINE-CVE-2019-12290

## Summary
Severity: High
Advisory: ALPINE-CVE-2019-12290
Ecosystem: Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2019-10-22
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-12290
Type: osv

## Affected
- Alpine:v3.12: `libidn2` — affected >=0 <2.2.0-r0
- Alpine:v3.13: `libidn2` — affected >=0 <2.2.0-r0
- Alpine:v3.14: `libidn2` — affected >=0 <2.2.0-r0
- Alpine:v3.15: `libidn2` — affected >=0 <2.2.0-r0
- Alpine:v3.16: `libidn2` — affected >=0 <2.2.0-r0
- Alpine:v3.17: `libidn2` — affected >=0 <2.2.0-r0
- Alpine:v3.18: `libidn2` — affected >=0 <2.2.0-r0
- Alpine:v3.19: `libidn2` — affected >=0 <2.2.0-r0
- Alpine:v3.20: `libidn2` — affected >=0 <2.2.0-r0
- Alpine:v3.21: `libidn2` — affected >=0 <2.2.0-r0
- Alpine:v3.22: `libidn2` — affected >=0 <2.2.0-r0
- Alpine:v3.23: `libidn2` — affected >=0 <2.2.0-r0
- Alpine:v3.24: `libidn2` — affected >=0 <2.2.0-r0

## Details
GNU libidn2 before 2.2.0 fails to perform the roundtrip checks specified in RFC3490 Section 4.2 when converting A-labels to U-labels. This makes it possible in some circumstances for one domain to impersonate another. By creating a malicious domain that matches a target domain except for the inclusion of certain punycoded Unicode characters (that would be discarded when converted first to a Unicode label and then back to an ASCII label), arbitrary domains can be impersonated.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-12290
