# [H] Improper Verification of Cryptographic Signature in PySAML2

## Summary
Severity: High
Advisory: GHSA-qf7v-8hj3-4xw7
CVE: CVE-2020-5390
CWE: CWE-347
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2020-05-06
Source: https://github.com/advisories/GHSA-qf7v-8hj3-4xw7
Type: github-advisory

## Affected
- PyPI: `pysaml2` — affected >=0 <5.0.0

## Details
PySAML2 before 5.0.0 does not check that the signature in a SAML document is enveloped and thus signature wrapping is effective, i.e., it is affected by XML Signature Wrapping (XSW). The signature information and the node/object that is signed can be in different places and thus the signature verification will succeed, but the wrong data will be used. This specifically affects the verification of assertions that have been signed.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-5390
- https://github.com/IdentityPython/pysaml2/commit/5e9d5acbcd8ae45c4e736ac521fd2df5b1c62e25
- https://github.com/IdentityPython/pysaml2/commit/f27c7e7a7010f83380566a219fd6a290a00f2b6e
- https://github.com/IdentityPython/pysaml2
- https://github.com/IdentityPython/pysaml2/blob/master/CHANGELOG.md#500-2020-01-13
- https://github.com/IdentityPython/pysaml2/releases
- https://github.com/IdentityPython/pysaml2/releases/tag/v5.0.0
- https://github.com/advisories/GHSA-qf7v-8hj3-4xw7
- https://github.com/pypa/advisory-database/tree/main/vulns/pysaml2/PYSEC-2020-94.yaml
- https://lists.debian.org/debian-lts-announce/2020/02/msg00025.html
- https://pypi.org/project/pysaml2/5.0.0
- https://usn.ubuntu.com/4245-1
- https://www.debian.org/security/2020/dsa-4630
