# [M] ALPINE-CVE-2019-14861

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2019-14861
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.3 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-12-10
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-14861
Type: osv

## Affected
- Alpine:v3.10: `samba` — affected >=4.0.0 <4.10.11-r0
- Alpine:v3.11: `samba` — affected >=4.0.0 <4.11.3-r0
- Alpine:v3.12: `samba` — affected >=4.0.0 <4.11.3-r0
- Alpine:v3.13: `samba` — affected >=4.0.0 <4.11.3-r0
- Alpine:v3.14: `samba` — affected >=4.0.0 <4.11.3-r0
- Alpine:v3.15: `samba` — affected >=4.0.0 <4.11.3-r0
- Alpine:v3.16: `samba` — affected >=4.0.0 <4.11.3-r0
- Alpine:v3.17: `samba` — affected >=4.0.0 <4.11.3-r0
- Alpine:v3.18: `samba` — affected >=4.0.0 <4.11.3-r0
- Alpine:v3.19: `samba` — affected >=4.0.0 <4.11.3-r0
- Alpine:v3.20: `samba` — affected >=4.0.0 <4.11.3-r0
- Alpine:v3.21: `samba` — affected >=4.0.0 <4.11.3-r0
- Alpine:v3.22: `samba` — affected >=4.0.0 <4.11.3-r0
- Alpine:v3.23: `samba` — affected >=4.0.0 <4.11.3-r0
- Alpine:v3.24: `samba` — affected >=4.0.0 <4.11.3-r0

## Details
All Samba versions 4.x.x before 4.9.17, 4.10.x before 4.10.11 and 4.11.x before 4.11.3 have an issue, where the (poorly named) dnsserver RPC pipe provides administrative facilities to modify DNS records and zones. Samba, when acting as an AD DC, stores DNS records in LDAP. In AD, the default permissions on the DNS partition allow creation of new records by authenticated users. This is used for example to allow machines to self-register in DNS. If a DNS record was created that case-insensitively matched the name of the zone, the ldb_qsort() and dns_name_compare() routines could be confused into reading memory prior to the list of DNS entries when responding to DnssrvEnumRecords() or DnssrvEnumRecords2() and so following invalid memory as a pointer.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-14861
