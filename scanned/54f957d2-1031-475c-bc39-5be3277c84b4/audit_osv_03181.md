# [C] ALPINE-CVE-2025-10230

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2025-10230
Ecosystem: Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 10.0 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2025-11-07
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-10230
Type: osv

## Affected
- Alpine:v3.22: `samba` — affected >=0 <4.21.9-r0
- Alpine:v3.23: `samba` — affected >=0 <4.21.9-r0
- Alpine:v3.24: `samba` — affected >=0 <4.21.9-r0

## Details
A flaw was found in Samba, in the front-end WINS hook handling: NetBIOS names from registration packets are passed to a shell without proper validation or escaping. Unsanitized NetBIOS name data from WINS registration packets are inserted into a shell command and executed by the Samba Active Directory Domain Controller’s wins hook, allowing an unauthenticated network attacker to achieve remote command execution as the Samba process.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-10230
