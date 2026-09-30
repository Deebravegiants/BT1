# [H] ALPINE-CVE-2026-2100

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-2100
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-03-26
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-2100
Type: osv

## Affected
- Alpine:v3.21: `p11-kit` — affected >=0 <0.26.2-r0
- Alpine:v3.22: `p11-kit` — affected >=0 <0.26.2-r0
- Alpine:v3.23: `p11-kit` — affected >=0 <0.26.2-r0
- Alpine:v3.24: `p11-kit` — affected >=0 <0.26.2-r0

## Details
A flaw was found in p11-kit. A remote attacker could exploit this vulnerability by calling the C_DeriveKey function on a remote token with specific IBM kyber or IBM btc derive mechanism parameters set to NULL. This could lead to the RPC-client attempting to return an uninitialized value, potentially resulting in a NULL dereference or undefined behavior. This issue may cause an application level denial of service or other unpredictable system states.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-2100
