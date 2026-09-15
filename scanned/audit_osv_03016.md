# [M] ALPINE-CVE-2024-2511

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2024-2511
Ecosystem: Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-04-08
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-2511
Type: osv

## Affected
- Alpine:v3.17: `openssl` — affected >=0 <3.0.12-r5
- Alpine:v3.18: `openssl` — affected >=0 <3.1.4-r6
- Alpine:v3.19: `openssl` — affected >=0 <3.1.4-r6
- Alpine:v3.20: `openssl` — affected >=0 <3.2.1-r2
- Alpine:v3.21: `openssl` — affected >=0 <3.2.1-r2
- Alpine:v3.22: `openssl` — affected >=0 <3.2.1-r2
- Alpine:v3.23: `openssl` — affected >=0 <3.2.1-r2
- Alpine:v3.24: `openssl` — affected >=0 <3.2.1-r2

## Details
Issue summary: Some non-default TLS server configurations can cause unbounded
memory growth when processing TLSv1.3 sessions

Impact summary: An attacker may exploit certain server configurations to trigger
unbounded memory growth that would lead to a Denial of Service

This problem can occur in TLSv1.3 if the non-default SSL_OP_NO_TICKET option is
being used (but not if early_data support is also configured and the default
anti-replay protection is in use). In this case, under certain conditions, the
session cache can get into an incorrect state and it will fail to flush properly
as it fills. The session cache will continue to grow in an unbounded manner. A
malicious client could deliberately create the scenario for this failure to
force a Denial of Service. It may also happen by accident in normal operation.

This issue only affects TLS servers supporting TLSv1.3. It does not affect TLS
clients.

The FIPS modules in 3.2, 3.1 and 3.0 are not affected by this issue. OpenSSL
1.0.2 is also not affected by this issue.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-2511
