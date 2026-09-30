# [M] ALPINE-CVE-2022-2928

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2022-2928
Ecosystem: Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20
CVSS: 6.5 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-10-07
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-2928
Type: osv

## Affected
- Alpine:v3.13: `dhcp` — affected >=4.4.0 <4.4.3_p1-r0
- Alpine:v3.14: `dhcp` — affected >=4.4.0 <4.4.3_p1-r0
- Alpine:v3.15: `dhcp` — affected >=4.4.0 <4.4.3_p1-r0
- Alpine:v3.16: `dhcp` — affected >=4.4.0 <4.4.3_p1-r0
- Alpine:v3.17: `dhcp` — affected >=4.4.0 <4.4.3_p1-r0
- Alpine:v3.18: `dhcp` — affected >=4.4.0 <4.4.3_p1-r0
- Alpine:v3.19: `dhcp` — affected >=4.4.0 <4.4.3_p1-r0
- Alpine:v3.20: `dhcp` — affected >=4.4.0 <4.4.3_p1-r0

## Details
In ISC DHCP 4.4.0 -> 4.4.3, ISC DHCP 4.1-ESV-R1 -> 4.1-ESV-R16-P1, when the function option_code_hash_lookup() is called from add_option(), it increases the option's refcount field. However, there is not a corresponding call to option_dereference() to decrement the refcount field. The function add_option() is only used in server responses to lease query packets. Each lease query response calls this function for several options, so eventually, the reference counters could overflow and cause the server to abort.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-2928
