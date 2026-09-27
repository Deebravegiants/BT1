# [M] wolfCrypt leaks cryptographic information via timing side channel

## Summary
Severity: Medium
Advisory: GHSA-q95h-vc86-hv77
CVE: CVE-2019-13628
CWE: CWE-203
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-q95h-vc86-hv77
Type: github-advisory

## Affected
- PyPI: `wolfcrypt` — affected >=0 <4.1.0

## Details
wolfSSL and wolfCrypt 4.0.0 and earlier (when configured without `--enable-fpecc`, `--enable-sp`, or` --enable-sp-math`) contain a timing side channel in ECDSA signature generation. This allows a local attacker, able to precisely measure the duration of signature operations, to infer information about the nonces used and potentially mount a lattice attack to recover the private key used. The issue occurs because ecc.c scalar multiplication might leak the bit length.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-13628
- https://eprint.iacr.org/2011/232.pdf
- https://github.com/wolfSSL/wolfcrypt-py
- https://minerva.crocs.fi.muni.cz
- https://tches.iacr.org/index.php/TCHES/article/view/7337
- http://www.openwall.com/lists/oss-security/2019/10/02/2
