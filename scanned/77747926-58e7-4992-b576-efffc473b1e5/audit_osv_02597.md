# [M] ALPINE-CVE-2022-3437

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2022-3437
Ecosystem: Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-01-12
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-3437
Type: osv

## Affected
- Alpine:v3.14: `heimdal` — affected >=0 <7.7.1-r0
- Alpine:v3.15: `heimdal` — affected >=0 <7.7.1-r0
- Alpine:v3.16: `heimdal` — affected >=0 <7.7.1-r0
- Alpine:v3.17: `heimdal` — affected >=0 <7.7.1-r0
- Alpine:v3.18: `heimdal` — affected >=0 <7.7.1-r0
- Alpine:v3.19: `heimdal` — affected >=0 <7.7.1-r0
- Alpine:v3.20: `heimdal` — affected >=0 <7.7.1-r0
- Alpine:v3.21: `heimdal` — affected >=0 <7.7.1-r0
- Alpine:v3.22: `heimdal` — affected >=0 <7.7.1-r0
- Alpine:v3.23: `heimdal` — affected >=0 <7.7.1-r0
- Alpine:v3.24: `heimdal` — affected >=0 <7.7.1-r0
- Alpine:v3.15: `samba` — affected >=4.0.0 <4.15.12-r0
- Alpine:v3.16: `samba` — affected >=4.0.0 <4.15.12-r0
- Alpine:v3.17: `samba` — affected >=4.0.0 <4.16.6-r0
- Alpine:v3.18: `samba` — affected >=4.0.0 <4.16.6-r0
- Alpine:v3.19: `samba` — affected >=4.0.0 <4.16.6-r0
- Alpine:v3.20: `samba` — affected >=4.0.0 <4.16.6-r0
- Alpine:v3.21: `samba` — affected >=4.0.0 <4.16.6-r0
- Alpine:v3.22: `samba` — affected >=4.0.0 <4.16.6-r0
- Alpine:v3.23: `samba` — affected >=4.0.0 <4.16.6-r0
- Alpine:v3.24: `samba` — affected >=4.0.0 <4.16.6-r0

## Details
A heap-based buffer overflow vulnerability was found in Samba within the GSSAPI unwrap_des() and unwrap_des3() routines of Heimdal. The DES and Triple-DES decryption routines in the Heimdal GSSAPI library allow a length-limited write buffer overflow on malloc() allocated memory when presented with a maliciously small packet. This flaw allows a remote user to send specially crafted malicious data to the application, possibly resulting in a denial of service (DoS) attack.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-3437
