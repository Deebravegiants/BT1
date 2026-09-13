# [M] ALPINE-CVE-2026-66046

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-66046
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-08-18
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-66046
Type: osv

## Affected
- Alpine:v3.21: `expat` — affected >=0 <2.8.4-r0
- Alpine:v3.22: `expat` — affected >=0 <2.8.4-r0
- Alpine:v3.23: `expat` — affected >=0 <2.8.4-r0
- Alpine:v3.24: `expat` — affected >=0 <2.8.4-r0

## Details
Expat through 2.8.3 contains a denial of service vulnerability caused by quadratic algorithmic complexity in the storeAtts() function in xmlparse.c, where processing N specified attributes with non-normalized values triggers an O(N^2) linear scan of elementType->defaultAtts to determine CDATA status. A remote unauthenticated attacker can supply a single well-formed XML document of a few megabytes to an application parsing untrusted XML to cause excessive CPU consumption, resulting in denial of service without requiring authentication, external entity resolution, or non-default parser options.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-66046
