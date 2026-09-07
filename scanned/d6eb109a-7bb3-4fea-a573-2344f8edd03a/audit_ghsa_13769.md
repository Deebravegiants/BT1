# [H] PyPinkSign uses a non-random or static IV for Cipher Block Chaining (CBC) mode in AES encryption

## Summary
Severity: High
Advisory: GHSA-fxff-wxxv-c2jc
CVE: CVE-2023-48056
CWE: CWE-330
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-11-16
Source: https://github.com/advisories/GHSA-fxff-wxxv-c2jc
Type: github-advisory

## Affected
- PyPI: `pypinksign` — affected >=0

## Details
PyPinkSign v0.5.1 uses a non-random or static IV for Cipher Block Chaining (CBC) mode in AES encryption. This vulnerability can lead to the disclosure of information and communications.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-48056
- https://github.com/bandoche/PyPinkSign/issues/29
- https://github.com/bandoche/PyPinkSign/commit/e1809ddf6a266e9007e10f0486b462fa7f89a43d
- https://github.com/bandoche/PyPinkSign
- https://github.com/bandoche/PyPinkSign/blob/main/pypinksign/pypinksign.py#L504
- https://github.com/bandoche/PyPinkSign/blob/main/pypinksign/pypinksign.py#L537
- https://github.com/pypa/advisory-database/tree/main/vulns/pypinksign/PYSEC-2023-245.yaml
- https://gxx777.github.io/PyPinkSign_v0.5.1_Cryptographic_API_Misuse_Vulnerability.md
