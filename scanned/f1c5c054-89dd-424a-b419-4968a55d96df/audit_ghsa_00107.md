# [H] PyCryptodome integer overflow vulnerability

## Summary
Severity: High
Advisory: GHSA-hgg3-g7gr-66r7
CVE: CVE-2018-15560
CWE: CWE-190
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2018-08-27
Source: https://github.com/advisories/GHSA-hgg3-g7gr-66r7
Type: github-advisory

## Affected
- PyPI: `pycryptodome` — affected >=0 <3.6.6

## Details
PyCryptodome before 3.6.6 has an integer overflow in the data_len variable in AESNI.c, related to the AESNI_encrypt and AESNI_decrypt functions, leading to the mishandling of messages shorter than 16 bytes.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-15560
- https://github.com/Legrandin/pycryptodome/issues/198
- https://github.com/Legrandin/pycryptodome
- https://github.com/advisories/GHSA-hgg3-g7gr-66r7
- https://github.com/pypa/advisory-database/tree/main/vulns/pycryptodome/PYSEC-2018-21.yaml
- https://whitehatck01.blogspot.com/2018/08/integer-overflow-vulnerability-in.html
