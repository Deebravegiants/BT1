# [M] ALPINE-CVE-2025-14819

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2025-14819
Ecosystem: Alpine:v3.23, Alpine:v3.24
CVSS: 5.3 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2026-01-08
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-14819
Type: osv

## Affected
- Alpine:v3.23: `curl` — affected >=7.87.0 <8.18.0-r0
- Alpine:v3.24: `curl` — affected >=7.87.0 <8.18.0-r0

## Details
When doing TLS related transfers with reused easy or multi handles and
altering the  `CURLSSLOPT_NO_PARTIALCHAIN` option, libcurl could accidentally
reuse a CA store cached in memory for which the partial chain option was
reversed. Contrary to the user's wishes and expectations. This could make
libcurl find and accept a trust chain that it otherwise would not.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-14819
