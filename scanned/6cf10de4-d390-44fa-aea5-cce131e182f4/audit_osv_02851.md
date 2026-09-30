# [C] ALPINE-CVE-2023-37920

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2023-37920
Ecosystem: Alpine:v3.18
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-07-25
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-37920
Type: osv

## Affected
- Alpine:v3.18: `py3-certifi` — affected >=2015.4.28 <2023.7.22-r0

## Details
Certifi is a curated collection of Root Certificates for validating the trustworthiness of SSL certificates while verifying the identity of TLS hosts. Certifi prior to version 2023.07.22 recognizes "e-Tugra" root certificates. e-Tugra's root certificates were subject to an investigation prompted by reporting of security issues in their systems. Certifi 2023.07.22 removes root certificates from "e-Tugra" from the root store.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-37920
