# [H] Observable Timing Discrepancy in pypqc

## Summary
Severity: High
Advisory: GHSA-hvh4-5qr6-3v7r
CWE: CWE-385, CWE-733
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N/E:P/RL:U/RC:C (CVSS_V3)
Published: 2024-06-05
Source: https://github.com/advisories/GHSA-hvh4-5qr6-3v7r
Type: github-advisory

## Affected
- PyPI: `pypqc` — affected >=0.0.4

## Details
### Impact
`kyber512`, `kyber768`, and `kyber1024` on Mac OS \(or when compiled with clang\) only: An attacker able to submit many decapsulation requests against a single private key, and to gain timing information about the decapsulation, could recover the private key. Proof-of-concept exploit exists for a local attacker.

CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N/E:P/RL:U/RC:C  

### Patches
No patch is currently available / pending upstream [PQClean#556](https://github.com/PQClean/PQClean/issues/556).

### Workarounds
No workarounds have been reported. The 0.0.7 -> 0.0.7.1 upgrade, when available, should be a drop-in replacement<!--; it has no known breaking changes-->.

### References

https://pqshield.com/pqshield-plugs-timing-leaks-in-kyber-ml-kem-to-improve-pqc-implementation-maturity/

https://github.com/antoonpurnal/clangover

https://www.github.com/PQClean/PQClean/issues/556

https://www.github.com/pq-crystals/kyber/commit/9b8d30698a3e7449aeb34e62339d4176f11e3c6c

## References
- https://github.com/JamesTheAwesomeDude/pypqc/security/advisories/GHSA-hvh4-5qr6-3v7r
- https://github.com/PQClean/PQClean/issues/556
- https://github.com/JamesTheAwesomeDude/pypqc
