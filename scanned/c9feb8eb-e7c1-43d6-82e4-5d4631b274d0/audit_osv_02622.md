# [C] ALPINE-CVE-2022-37454

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2022-37454
Ecosystem: Alpine:v3.16, Alpine:v3.17
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-10-21
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-37454
Type: osv

## Affected
- Alpine:v3.16: `python3` — affected >=0 <3.10.9-r0
- Alpine:v3.17: `python3` — affected >=0 <3.10.9-r0

## Details
The Keccak XKCP SHA-3 reference implementation before fdc6fef has an integer overflow and resultant buffer overflow that allows attackers to execute arbitrary code or eliminate expected cryptographic properties. This occurs in the sponge function interface.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-37454
