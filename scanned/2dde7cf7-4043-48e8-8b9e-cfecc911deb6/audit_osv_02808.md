# [H] ALPINE-CVE-2023-28319

## Summary
Severity: High
Advisory: ALPINE-CVE-2023-28319
Ecosystem: Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-05-26
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-28319
Type: osv

## Affected
- Alpine:v3.15: `curl` — affected >=0 <8.1.0-r0
- Alpine:v3.16: `curl` — affected >=0 <8.1.0-r0
- Alpine:v3.17: `curl` — affected >=0 <8.1.0-r0
- Alpine:v3.18: `curl` — affected >=0 <8.1.0-r0
- Alpine:v3.19: `curl` — affected >=0 <8.1.0-r0
- Alpine:v3.20: `curl` — affected >=0 <8.1.0-r0
- Alpine:v3.21: `curl` — affected >=0 <8.1.0-r0
- Alpine:v3.22: `curl` — affected >=0 <8.1.0-r0
- Alpine:v3.23: `curl` — affected >=0 <8.1.0-r0
- Alpine:v3.24: `curl` — affected >=0 <8.1.0-r0

## Details
A use after free vulnerability exists in curl <v8.1.0 in the way libcurl offers a feature to verify an SSH server's public key using a SHA 256 hash. When this check fails, libcurl would free the memory for the fingerprint before it returns an error message containing the (now freed) hash. This flaw risks inserting sensitive heap-based data into the error message that might be shown to users or otherwise get leaked and revealed.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-28319
