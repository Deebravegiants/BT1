# [H] ALPINE-CVE-2026-21863

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-21863
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-02-23
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-21863
Type: osv

## Affected
- Alpine:v3.21: `valkey` — affected >=8.0.0 <7.2.12-r0
- Alpine:v3.22: `valkey` — affected >=8.0.0 <8.1.6-r0
- Alpine:v3.23: `valkey` — affected >=8.0.0 <9.0.3-r0
- Alpine:v3.24: `valkey` — affected >=8.0.0 <9.0.3-r0

## Details
Valkey is a distributed key-value database. Prior to versions 9.0.2, 8.1.6, 8.0.7, and 7.2.12, a malicious actor with access to the Valkey clusterbus port can send an invalid packet that may cause an out bound read, which might result in the system crashing. The Valkey clusterbus packet processing code does not validate that a clusterbus ping extension packet is located within buffer of the clusterbus packet before attempting to read it. Versions 9.0.2, 8.1.6, 8.0.7, and 7.2.12 fix the issue. As an additional mitigation, don't expose the cluster bus connection directly to end users, and protect the connection with its own network ACLs.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-21863
