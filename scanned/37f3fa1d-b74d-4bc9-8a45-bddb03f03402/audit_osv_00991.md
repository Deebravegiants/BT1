# [C] ALPINE-CVE-2018-14618

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2018-14618
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-09-05
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-14618
Type: osv

## Affected
- Alpine:v3.10: `curl` — affected >=0 <7.61.1-r0
- Alpine:v3.11: `curl` — affected >=0 <7.61.1-r0
- Alpine:v3.12: `curl` — affected >=0 <7.61.1-r0
- Alpine:v3.13: `curl` — affected >=0 <7.61.1-r0
- Alpine:v3.14: `curl` — affected >=0 <7.61.1-r0
- Alpine:v3.15: `curl` — affected >=0 <7.61.1-r0
- Alpine:v3.16: `curl` — affected >=0 <7.61.1-r0
- Alpine:v3.17: `curl` — affected >=0 <7.61.1-r0
- Alpine:v3.18: `curl` — affected >=0 <7.61.1-r0
- Alpine:v3.19: `curl` — affected >=0 <7.61.1-r0
- Alpine:v3.20: `curl` — affected >=0 <7.61.1-r0
- Alpine:v3.21: `curl` — affected >=0 <7.61.1-r0
- Alpine:v3.22: `curl` — affected >=0 <7.61.1-r0
- Alpine:v3.23: `curl` — affected >=0 <7.61.1-r0
- Alpine:v3.24: `curl` — affected >=0 <7.61.1-r0
- Alpine:v3.5: `curl` — affected >=0 <7.61.1-r0
- Alpine:v3.6: `curl` — affected >=0 <7.61.1-r0
- Alpine:v3.7: `curl` — affected >=0 <7.61.1-r0
- Alpine:v3.8: `curl` — affected >=0 <7.61.1-r0
- Alpine:v3.9: `curl` — affected >=0 <7.61.1-r0

## Details
curl before version 7.61.1 is vulnerable to a buffer overrun in the NTLM authentication code. The internal function Curl_ntlm_core_mk_nt_hash multiplies the length of the password by two (SUM) to figure out how large temporary storage area to allocate from the heap. The length value is then subsequently used to iterate over the password and generate output into the allocated storage buffer. On systems with a 32 bit size_t, the math to calculate SUM triggers an integer overflow when the password length exceeds 2GB (2^31 bytes). This integer overflow usually causes a very small buffer to actually get allocated instead of the intended very huge one, making the use of that buffer end up in a heap buffer overflow. (This bug is almost identical to CVE-2017-8816.)

## References
- https://security.alpinelinux.org/vuln/CVE-2018-14618
