# [C] ALPINE-CVE-2021-25216

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2021-25216
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-04-29
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-25216
Type: osv

## Affected
- Alpine:v3.10: `bind` — affected >=9.0.0 <9.16.15-r0
- Alpine:v3.11: `bind` — affected >=9.0.0 <9.16.15-r0
- Alpine:v3.12: `bind` — affected >=9.0.0 <9.16.15-r0
- Alpine:v3.13: `bind` — affected >=9.0.0 <9.16.15-r0
- Alpine:v3.14: `bind` — affected >=9.0.0 <9.16.15-r0
- Alpine:v3.15: `bind` — affected >=9.0.0 <9.16.15-r0
- Alpine:v3.16: `bind` — affected >=9.0.0 <9.16.15-r0
- Alpine:v3.17: `bind` — affected >=9.0.0 <9.16.15-r0
- Alpine:v3.18: `bind` — affected >=9.0.0 <9.16.15-r0
- Alpine:v3.19: `bind` — affected >=9.0.0 <9.16.15-r0
- Alpine:v3.20: `bind` — affected >=9.0.0 <9.16.15-r0
- Alpine:v3.21: `bind` — affected >=9.0.0 <9.16.15-r0
- Alpine:v3.22: `bind` — affected >=9.0.0 <9.16.15-r0
- Alpine:v3.23: `bind` — affected >=9.0.0 <9.16.15-r0
- Alpine:v3.24: `bind` — affected >=9.0.0 <9.16.15-r0

## Details
In BIND 9.5.0 -> 9.11.29, 9.12.0 -> 9.16.13, and versions BIND 9.11.3-S1 -> 9.11.29-S1 and 9.16.8-S1 -> 9.16.13-S1 of BIND Supported Preview Edition, as well as release versions 9.17.0 -> 9.17.1 of the BIND 9.17 development branch, BIND servers are vulnerable if they are running an affected version and are configured to use GSS-TSIG features. In a configuration which uses BIND's default settings the vulnerable code path is not exposed, but a server can be rendered vulnerable by explicitly setting values for the tkey-gssapi-keytab or tkey-gssapi-credential configuration options. Although the default configuration is not vulnerable, GSS-TSIG is frequently used in networks where BIND is integrated with Samba, as well as in mixed-server environments that combine BIND servers with Active Directory domain controllers. For servers that meet these conditions, the ISC SPNEGO implementation is vulnerable to various attacks, depending on the CPU architecture for which BIND was built: For named binaries compiled for 64-bit platforms, this flaw can be used to trigger a buffer over-read, leading to a server crash. For named binaries compiled for 32-bit platforms, this flaw can be used to trigger a server crash due to a buffer overflow and possibly also to achieve remote code execution. We have determined that standard SPNEGO implementations are available in the MIT and Heimdal Kerberos libraries, which support a broad range of operating systems, rendering the ISC implementation unnecessary and obsolete. Therefore, to reduce the attack surface for BIND users, we will be removing the ISC SPNEGO implementation in the April releases of BIND 9.11 and 9.16 (it had already been dropped from BIND 9.17). We would not normally remove something from a stable ESV (Extended Support Version) of BIND, but since system libraries can replace the ISC SPNEGO implementation, we have made an exception in this case for reasons of stability and security.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-25216
