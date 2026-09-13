# [H] ALPINE-CVE-2017-11103

## Summary
Severity: High
Advisory: ALPINE-CVE-2017-11103
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.3, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-07-13
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-11103
Type: osv

## Affected
- Alpine:v3.10: `heimdal` — affected >=0 <7.4.0-r0
- Alpine:v3.11: `heimdal` — affected >=0 <7.4.0-r0
- Alpine:v3.12: `heimdal` — affected >=0 <7.4.0-r0
- Alpine:v3.13: `heimdal` — affected >=0 <7.4.0-r0
- Alpine:v3.14: `heimdal` — affected >=0 <7.4.0-r0
- Alpine:v3.15: `heimdal` — affected >=0 <7.4.0-r0
- Alpine:v3.16: `heimdal` — affected >=0 <7.4.0-r0
- Alpine:v3.17: `heimdal` — affected >=0 <7.4.0-r0
- Alpine:v3.18: `heimdal` — affected >=0 <7.4.0-r0
- Alpine:v3.19: `heimdal` — affected >=0 <7.4.0-r0
- Alpine:v3.20: `heimdal` — affected >=0 <7.4.0-r0
- Alpine:v3.21: `heimdal` — affected >=0 <7.4.0-r0
- Alpine:v3.22: `heimdal` — affected >=0 <7.4.0-r0
- Alpine:v3.23: `heimdal` — affected >=0 <7.4.0-r0
- Alpine:v3.24: `heimdal` — affected >=0 <7.4.0-r0
- Alpine:v3.3: `heimdal` — affected >=0 <1.6_rc2-r5
- Alpine:v3.4: `heimdal` — affected >=0 <1.6_rc2-r5
- Alpine:v3.5: `heimdal` — affected >=0 <1.6_rc2-r6
- Alpine:v3.6: `heimdal` — affected >=0 <7.1.0-r1
- Alpine:v3.7: `heimdal` — affected >=0 <7.4.0-r0
- Alpine:v3.8: `heimdal` — affected >=0 <7.4.0-r0
- Alpine:v3.9: `heimdal` — affected >=0 <7.4.0-r0
- Alpine:v3.3: `samba` — affected >=4.0.0 <4.2.14-r4
- Alpine:v3.4: `samba` — affected >=4.0.0 <4.4.14-r1
- Alpine:v3.5: `samba` — affected >=4.0.0 <4.5.10-r1

## Details
Heimdal before 7.4 allows remote attackers to impersonate services with Orpheus' Lyre attacks because it obtains service-principal names in a way that violates the Kerberos 5 protocol specification. In _krb5_extract_ticket() the KDC-REP service name must be obtained from the encrypted version stored in 'enc_part' instead of the unencrypted version stored in 'ticket'. Use of the unencrypted version provides an opportunity for successful server impersonation and other attacks. NOTE: this CVE is only for Heimdal and other products that embed Heimdal code; it does not apply to other instances in which this part of the Kerberos 5 protocol specification is violated.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-11103
