# [M] ALPINE-CVE-2024-0853

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2024-0853
Ecosystem: Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2024-02-03
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-0853
Type: osv

## Affected
- Alpine:v3.17: `curl` — affected >=0 <8.6.0-r0
- Alpine:v3.18: `curl` — affected >=0 <8.6.0-r0
- Alpine:v3.19: `curl` — affected >=0 <8.6.0-r0
- Alpine:v3.20: `curl` — affected >=0 <8.6.0-r0
- Alpine:v3.21: `curl` — affected >=0 <8.6.0-r0
- Alpine:v3.22: `curl` — affected >=0 <8.6.0-r0
- Alpine:v3.23: `curl` — affected >=0 <8.6.0-r0
- Alpine:v3.24: `curl` — affected >=0 <8.6.0-r0

## Details
curl inadvertently kept the SSL session ID for connections in its cache even when the verify status (*OCSP stapling*) test failed. A subsequent transfer to
the same hostname could then succeed if the session ID cache was still fresh, which then skipped the verify status check.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-0853
