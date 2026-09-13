# [H] Python-RSA decryption of ciphertext leads to DoS

## Summary
Severity: High
Advisory: GHSA-537h-rv9q-vvph
CVE: CVE-2020-13757
CWE: CWE-327
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2021-03-24
Source: https://github.com/advisories/GHSA-537h-rv9q-vvph
Type: github-advisory

## Affected
- PyPI: `rsa` — affected >=0 <4.1

## Details
Python-RSA before 4.1 ignores leading '\0' bytes during decryption of ciphertext. This could conceivably have a security-relevant impact, e.g., by helping an attacker to infer that an application uses Python-RSA, or if the length of accepted ciphertext affects application behavior (such as by causing excessive memory allocation).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-13757
- https://github.com/sybrenstuvel/python-rsa/issues/146
- https://github.com/sybrenstuvel/python-rsa/issues/146#issuecomment-641845667
- https://github.com/pypa/advisory-database/tree/main/vulns/rsa/PYSEC-2020-99.yaml
- https://github.com/sybrenstuvel/python-rsa
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/2KILTHBHNSDUCYV22ODLOKTICJJ7JQIQ
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/ZYB65VNILRBTXL6EITQTH2PZPK7I23MW
- https://usn.ubuntu.com/4478-1
