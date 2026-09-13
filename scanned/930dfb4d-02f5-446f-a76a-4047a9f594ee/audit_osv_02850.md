# [H] ALPINE-CVE-2023-37457

## Summary
Severity: High
Advisory: ALPINE-CVE-2023-37457
Ecosystem: Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:H)
Published: 2023-12-14
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-37457
Type: osv

## Affected
- Alpine:v3.16: `asterisk` — affected >=19.0.0 <18.20.2-r0
- Alpine:v3.17: `asterisk` — affected >=19.0.0 <18.20.2-r0
- Alpine:v3.18: `asterisk` — affected >=19.0.0 <18.20.2-r0
- Alpine:v3.19: `asterisk` — affected >=19.0.0 <20.5.1-r0
- Alpine:v3.20: `asterisk` — affected >=19.0.0 <20.5.1-r0
- Alpine:v3.21: `asterisk` — affected >=19.0.0 <20.5.1-r0
- Alpine:v3.22: `asterisk` — affected >=19.0.0 <20.5.1-r0
- Alpine:v3.23: `asterisk` — affected >=19.0.0 <20.5.1-r0
- Alpine:v3.24: `asterisk` — affected >=19.0.0 <20.5.1-r0

## Details
Asterisk is an open source private branch exchange and telephony toolkit. In Asterisk versions 18.20.0 and prior, 20.5.0 and prior, and 21.0.0; as well as ceritifed-asterisk 18.9-cert5 and prior, the 'update' functionality of the PJSIP_HEADER dialplan function can exceed the available buffer space for storing the new value of a header. By doing so this can overwrite memory or cause a crash. This is not externally exploitable, unless dialplan is explicitly written to update a header based on data from an outside source. If the 'update' functionality is not used the vulnerability does not occur. A patch is available at commit a1ca0268254374b515fa5992f01340f7717113fa.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-37457
