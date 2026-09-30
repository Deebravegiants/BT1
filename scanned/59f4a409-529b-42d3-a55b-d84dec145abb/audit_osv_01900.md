# [H] ALPINE-CVE-2020-25692

## Summary
Severity: High
Advisory: ALPINE-CVE-2020-25692
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.9
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-12-08
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-25692
Type: osv

## Affected
- Alpine:v3.10: `openldap` — affected >=0 <2.4.48-r2
- Alpine:v3.11: `openldap` — affected >=0 <2.4.48-r3
- Alpine:v3.12: `openldap` — affected >=0 <2.4.50-r1
- Alpine:v3.9: `openldap` — affected >=0 <2.4.48-r2

## Details
A NULL pointer dereference was found in OpenLDAP server and was fixed in openldap 2.4.55, during a request for renaming RDNs. An unauthenticated attacker could remotely crash the slapd process by sending a specially crafted request, causing a Denial of Service.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-25692
