# [M] Mbed TLS may use a low entropy PRNG seed

## Summary
Severity: Medium
Advisory: JLSEC-2026-465
Ecosystem: Julia
CVSS: 6.7 (CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-05-07
Source: https://osv.dev/vulnerability/JLSEC-2026-465
Type: osv

## Affected
- Julia: `MbedTLS_jll` — affected unspecified

## Details
An issue was discovered in Mbed TLS before 3.6.6 and 4.x before 4.1.0 and TF-PSA-Crypto before 1.1.0. There is a Predictable Seed in a Pseudo-Random Number Generator (PRNG).

## References
- https://github.com/advisories/GHSA-rjq9-c3rf-c638
- https://mbed-tls.readthedocs.io/en/latest/security-advisories
- https://mbed-tls.readthedocs.io/en/latest/security-advisories/
- https://mbed-tls.readthedocs.io/en/latest/security-advisories/mbedtls-security-advisory-2026-03-dev-random
- https://mbed-tls.readthedocs.io/en/latest/security-advisories/mbedtls-security-advisory-2026-03-dev-random/
- https://nvd.nist.gov/vuln/detail/CVE-2026-34871
