# [H] fastschema - Unauthenticated NULL Pointer Dereference DoS in Account Recovery Endpoint

## Summary
Severity: High
Advisory: CVE-2026-72582
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-72582
Type: osv

## Details
A NULL pointer dereference vulnerability in fastschema through v0.15.1 allows an unauthenticated remote attacker to crash the server process with a single HTTP request. The sendOTPEmail function in pkg/auth/local.go dereferences a pointer obtained from an unchecked error path without validating it is non-nil, causing a fatal panic that terminates the entire server when a recovery request is sent to the /api/auth/local/recover endpoint.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72582.json
- https://github.com/fastschema/fastschema
- https://nvd.nist.gov/vuln/detail/CVE-2026-72582
- https://github.com/fastschema/fastschema/blob/main/pkg/auth/local.go
