# [M] A 1-byte stack buffer over-read was identified in the MatchDomainName function (`src/internal.c`)...

## Summary
Severity: Medium
Advisory: JLSEC-2026-740
Ecosystem: Julia
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2026-07-14
Source: https://osv.dev/vulnerability/JLSEC-2026-740
Type: osv

## Affected
- Julia: `wolfSSL_jll` — affected >=0 <5.9.2+0

## Details
A 1-byte stack buffer over-read was identified in the MatchDomainName function (`src/internal.c`) during wildcard hostname validation when the `LEFT_MOST_WILDCARD_ONLY` flag is active.  If a wildcard * exhausts the entire hostname string, the function reads one byte past the buffer without a bounds check, which could cause a crash.

## References
- https://github.com/advisories/GHSA-6v2v-jgg9-h79w
- https://github.com/wolfSSL/wolfssl/pull/10119
- https://nvd.nist.gov/vuln/detail/CVE-2026-5772
