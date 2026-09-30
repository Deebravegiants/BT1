# [H] ALPINE-CVE-2023-42118

## Summary
Severity: High
Advisory: ALPINE-CVE-2023-42118
Ecosystem: Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-03
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-42118
Type: osv

## Affected
- Alpine:v3.18: `libspf2` — affected >=0 <1.2.11-r3
- Alpine:v3.19: `libspf2` — affected >=0 <1.2.11-r3
- Alpine:v3.20: `libspf2` — affected >=0 <1.2.11-r3
- Alpine:v3.21: `libspf2` — affected >=0 <1.2.11-r3
- Alpine:v3.22: `libspf2` — affected >=0 <1.2.11-r3
- Alpine:v3.23: `libspf2` — affected >=0 <1.2.11-r3
- Alpine:v3.24: `libspf2` — affected >=0 <1.2.11-r3

## Details
Exim libspf2 Integer Underflow Remote Code Execution Vulnerability. This vulnerability allows network-adjacent attackers to execute arbitrary code on affected installations of Exim libspf2. Authentication is not required to exploit this vulnerability. 

The specific flaw exists within the parsing of SPF macros. When parsing SPF macros, the process does not properly validate user-supplied data, which can result in an integer underflow before writing to memory. An attacker can leverage this vulnerability to execute code in the context of the service account.
. Was ZDI-CAN-17578.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-42118
