# [C] Mbed TLS peer can force the FFDH shared secret into a small set of values

## Summary
Severity: Critical
Advisory: JLSEC-2026-466
Ecosystem: Julia
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-05-07
Source: https://osv.dev/vulnerability/JLSEC-2026-466
Type: osv

## Affected
- Julia: `MbedTLS_jll` — affected unspecified

## Details
An issue was discovered in Mbed TLS 3.5.x and 3.6.x through 3.6.5 and TF-PSA-Crypto 1.0. There is a lack of contributory behavior in FFDH due to improper input validation. Using finite-field Diffie-Hellman, the other party can force the shared secret into a small set of values (lack of contributory behavior). This is a problem for protocols that depend on contributory behavior (which is not the case for TLS). The attack can be carried by the peer, or depending on the protocol by an active network attacker (person in the middle).

## References
- https://github.com/advisories/GHSA-347r-37hj-5jc9
- https://mbed-tls.readthedocs.io/en/latest/security-advisories
- https://mbed-tls.readthedocs.io/en/latest/security-advisories/
- https://mbed-tls.readthedocs.io/en/latest/security-advisories/mbedtls-security-advisory-2026-03-ffdh-peerkey-checks
- https://mbed-tls.readthedocs.io/en/latest/security-advisories/mbedtls-security-advisory-2026-03-ffdh-peerkey-checks/
- https://nvd.nist.gov/vuln/detail/CVE-2026-34872
