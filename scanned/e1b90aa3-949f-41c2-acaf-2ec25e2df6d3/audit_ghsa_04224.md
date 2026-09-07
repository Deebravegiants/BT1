# [H] Vulnerable OpenSSL included in cryptography wheels

## Summary
Severity: High
Advisory: GHSA-537c-gmf6-5ccf
CWE: CWE-125, CWE-1395
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-06-15
Source: https://github.com/advisories/GHSA-537c-gmf6-5ccf
Type: github-advisory

## Affected
- PyPI: `cryptography` — affected >=0.5.0 <48.0.1

## Details
pyca/cryptography's wheels include a statically linked copy of OpenSSL. The versions of OpenSSL included in wheels prior to cryptograph 48.01 are vulnerable to a security issue. More details about the vulnerability itself can be found in https://openssl-library.org/news/secadv/20260609.txt.

If you are building cryptography source ("sdist") then you are responsible for upgrading your copy of OpenSSL. Only users installing from wheels built by the cryptography project (i.e., those distributed on PyPI) need to update their cryptography versions.

## References
- https://github.com/pyca/cryptography/security/advisories/GHSA-537c-gmf6-5ccf
- https://github.com/pyca/cryptography
- https://openssl-library.org/news/secadv/20260609.txt
