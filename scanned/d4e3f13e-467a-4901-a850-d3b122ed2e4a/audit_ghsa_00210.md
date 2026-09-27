# [H] Pycrypto generates weak key parameters

## Summary
Severity: High
Advisory: GHSA-6528-wvf6-f6qg
CVE: CVE-2018-6594
CWE: CWE-326
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2018-07-12
Source: https://github.com/advisories/GHSA-6528-wvf6-f6qg
Type: github-advisory

## Affected
- PyPI: `pycrypto` — affected >=0

## Details
lib/Crypto/PublicKey/ElGamal.py in PyCrypto through 2.6.1 generates weak ElGamal key parameters, which allows attackers to obtain sensitive information by reading ciphertext data (i.e., it does not have semantic security in face of a ciphertext-only attack). The Decisional Diffie-Hellman (DDH) assumption does not hold for PyCrypto's ElGamal implementation.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-6594
- https://github.com/dlitz/pycrypto/issues/253
- https://github.com/TElgamal/attack-on-pycrypto-elgamal
- https://github.com/advisories/GHSA-6528-wvf6-f6qg
- https://github.com/dlitz/pycrypto
- https://github.com/pypa/advisory-database/tree/main/vulns/pycrypto/PYSEC-2018-97.yaml
- https://lists.debian.org/debian-lts-announce/2018/02/msg00018.html
- https://security.gentoo.org/glsa/202007-62
- https://usn.ubuntu.com/3616-1
- https://usn.ubuntu.com/3616-2
