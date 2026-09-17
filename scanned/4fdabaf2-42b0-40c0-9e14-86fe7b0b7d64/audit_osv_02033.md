# [H] ALPINE-CVE-2020-8625

## Summary
Severity: High
Advisory: ALPINE-CVE-2020-8625
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-02-17
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-8625
Type: osv

## Affected
- Alpine:v3.10: `bind` — affected >=9.5.0 <9.16.11-r2
- Alpine:v3.11: `bind` — affected >=9.5.0 <9.16.11-r2
- Alpine:v3.12: `bind` — affected >=9.5.0 <9.16.11-r2
- Alpine:v3.13: `bind` — affected >=9.5.0 <9.16.11-r2
- Alpine:v3.14: `bind` — affected >=9.5.0 <9.16.11-r2
- Alpine:v3.15: `bind` — affected >=9.5.0 <9.16.11-r2
- Alpine:v3.16: `bind` — affected >=9.5.0 <9.16.11-r2
- Alpine:v3.17: `bind` — affected >=9.5.0 <9.16.11-r2
- Alpine:v3.18: `bind` — affected >=9.5.0 <9.16.11-r2
- Alpine:v3.19: `bind` — affected >=9.5.0 <9.16.11-r2
- Alpine:v3.20: `bind` — affected >=9.5.0 <9.16.11-r2
- Alpine:v3.21: `bind` — affected >=9.5.0 <9.16.11-r2
- Alpine:v3.22: `bind` — affected >=9.5.0 <9.16.11-r2
- Alpine:v3.23: `bind` — affected >=9.5.0 <9.16.11-r2
- Alpine:v3.24: `bind` — affected >=9.5.0 <9.16.11-r2

## Details
BIND servers are vulnerable if they are running an affected version and are configured to use GSS-TSIG features. In a configuration which uses BIND's default settings the vulnerable code path is not exposed, but a server can be rendered vulnerable by explicitly setting valid values for the tkey-gssapi-keytab or tkey-gssapi-credentialconfiguration options. Although the default configuration is not vulnerable, GSS-TSIG is frequently used in networks where BIND is integrated with Samba, as well as in mixed-server environments that combine BIND servers with Active Directory domain controllers. The most likely outcome of a successful exploitation of the vulnerability is a crash of the named process. However, remote code execution, while unproven, is theoretically possible. Affects: BIND 9.5.0 -> 9.11.27, 9.12.0 -> 9.16.11, and versions BIND 9.11.3-S1 -> 9.11.27-S1 and 9.16.8-S1 -> 9.16.11-S1 of BIND Supported Preview Edition. Also release versions 9.17.0 -> 9.17.1 of the BIND 9.17 development branch

## References
- https://security.alpinelinux.org/vuln/CVE-2020-8625
