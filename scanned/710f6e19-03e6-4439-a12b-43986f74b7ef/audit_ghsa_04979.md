# [M] Cloudflare Quiche: Use-after-free in connection ID iterator FFI functions

## Summary
Severity: Medium
Advisory: GHSA-mh64-ph39-mrc9
CVE: CVE-2026-11941
CWE: CWE-416
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-mh64-ph39-mrc9
Type: github-advisory

## Affected
- crates.io: `quiche` — affected >=0.20.0 <0.29.2

## Details
### Impact

Cloudflare Quiche was affected by 2 use-after-free vulnerabilities in the connection ID iterator FFI functions.

The `quiche_connection_id_iter_next` and `quiche_conn_retired_scid_next` functions would return a pointer to a `ConnectionId` to the applications via function arguments, but the the owned `ConnectionId` would be dropped at the end of those functions' scope.

Only applications using those FFI functions are affected. The FFI API is disabled by default by a build-time feature flag.

quiche 0.29.2 is the earliest version containing the fix for this issue.

## References
- https://github.com/cloudflare/quiche/security/advisories/GHSA-mh64-ph39-mrc9
- https://nvd.nist.gov/vuln/detail/CVE-2026-11941
- https://github.com/cloudflare/quiche
