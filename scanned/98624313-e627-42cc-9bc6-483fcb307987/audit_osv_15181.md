# [M] CVE-2019-14317

## Summary
Severity: Medium
Advisory: CVE-2019-14317
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2019-12-11
Source: https://osv.dev/vulnerability/CVE-2019-14317
Type: osv

## Details
wolfSSL and wolfCrypt 4.1.0 and earlier (formerly known as CyaSSL) generate biased DSA nonces. This allows a remote attacker to compute the long term private key from several hundred DSA signatures via a lattice attack. The issue occurs because dsa.c fixes two bits of the generated nonces.

## References
- https://www.wolfssl.com/docs/security-vulnerabilities/
