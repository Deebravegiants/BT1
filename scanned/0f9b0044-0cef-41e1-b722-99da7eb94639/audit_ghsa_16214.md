# [H] pypqc private key retrieval vulnerability

## Summary
Severity: High
Advisory: GHSA-rc4p-p3j9-6577
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2024-02-22
Source: https://github.com/advisories/GHSA-rc4p-p3j9-6577
Type: github-advisory

## Affected
- PyPI: `pypqc` — affected >=0.0.4 <0.0.6.1

## Details
### Impact
`kyber512`, `kyber768`, and `kyber1024` only: An attacker able to submit many decapsulation requests against a single private key, and to gain timing information about the decapsulation, could recover the private key. Proof-of-concept exploit exists for a local attacker.

CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N/E:P/RL:O/RC:C  

### Patches
Version 0.0.6.1 and newer of PyPQC is patched.

### Workarounds
No workarounds have been reported. The 0.0.6 -> 0.0.6.1 upgrade should be a drop-in replacement; it has no known breaking changes.

### References
#### Timeline
1. Cryspen researchers privately reported KyberSlash to the reference implementation maintainers.

2. Peter Schwabe partially patched KyberSlash \(only "KyberSlash 1"\) in the reference implementation on December 1st, 2023, but did not document or advertise this as a security patch.  
   https://www.github.com/pq-crystals/kyber/commit/dda29cc63af721981ee2c831cf00822e69be3220

3. Daniel J. Bernstein publicly reported KyberSlash as a security issue on December 15th, 2023.  
   https://groups.google.com/a/list.nist.gov/g/pqc-forum/c/hWqFJCucuj4/m/-Z-jm_k9AAAJ

4. Daniel J. Bernstein created a webpage for authoritative reference about KyberSlash on December 19th, 2023.  
   https://kyberslash.cr.yp.to/

5. Thom Wiggers acknowledged KyberSlash as a security issue on December 19th, 2023.  
   https://www.github.com/PQClean/PQClean/issues/533

6. Prasanna Ravi and Matthias Kannwischer privately reported further details about KyberSlash \("KyberSlash 2"\) to the reference implementation maintainers.

7. Peter Schwabe completely patched KyberSlash in the reference implementation on December 29th, 2023.
   https://www.github.com/pq-crystals/kyber/commit/11d00ff1f20cfca1f72d819e5a45165c1e0a2816

8. Prasanna Ravi and Matthias Kannwischer publicly reported their findings \("KyberSlash 2"\) on December 30th, 2023.  
   https://groups.google.com/a/list.nist.gov/g/pqc-forum/c/ldX0ThYJuBo/m/ovODsdY7AwAJ

9. Daniel J. Bernstein published a proof-of-concept exploit \(only validated for a local attacker\) for KyberSlash on December 30th, 2023.  
   https://groups.google.com/a/list.nist.gov/g/pqc-forum/c/ldX0ThYJuBo/m/uIOqRF5BAwAJ

10. Thom Wiggers completely patched KyberSlash in PQClean on January 25th, 2024.  
   https://www.github.com/PQClean/PQClean/commit/3b43bc6fe46fe47be38f87af5019a7f1462ae6dd

11. James E. A. completely patched KyberSlash in pypqc and released a security update on January 26th, 2024.  
   https://www.github.com/JamesTheAwesomeDude/pypqc/commit/b33fec8cd36e865f8db6215c64b2d01f429a1ed6

## References
- https://github.com/JamesTheAwesomeDude/pypqc/security/advisories/GHSA-rc4p-p3j9-6577
- https://github.com/JamesTheAwesomeDude/pypqc
- https://groups.google.com/a/list.nist.gov/g/pqc-forum/c/hWqFJCucuj4/m/-Z-jm_k9AAAJ
- https://groups.google.com/a/list.nist.gov/g/pqc-forum/c/ldX0ThYJuBo/m/uIOqRF5BAwAJ
- https://kyberslash.cr.yp.to
- https://www.github.com/JamesTheAwesomeDude/pypqc/commit/b33fec8cd36e865f8db6215c64b2d01f429a1ed6
- https://www.github.com/PQClean/PQClean/issues/533
- https://www.github.com/PQClean/PQClean/pull/534#event-11595728485
- https://www.github.com/pq-crystals/kyber/commit/11d00ff1f20cfca1f72d819e5a45165c1e0a2816
- https://www.github.com/pq-crystals/kyber/commit/dda29cc63af721981ee2c831cf00822e69be3220
