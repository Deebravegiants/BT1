# [H] Python Keyring does not securely initialize encryption cipher

## Summary
Severity: High
Advisory: GHSA-p3h7-3c45-qj4v
CVE: CVE-2012-4571
CWE: CWE-326
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-p3h7-3c45-qj4v
Type: github-advisory

## Affected
- PyPI: `keyring` — affected >=0 <0.9.2

## Details
Python Keyring 0.9.1 does not securely initialize the cipher when encrypting passwords for `CryptedFileKeyring` files, which makes it easier for local users to obtain passwords via a brute-force attack.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2012-4571
- https://github.com/jaraco/keyring/commit/162f2ed0e39e16d561732b9fad8af6cd2341d7bd
- https://github.com/jaraco/keyring/commit/56272d908ba7a3fe4ebb6d6e87a7cc569f4726ac
- https://github.com/jaraco/keyring/commit/a76942672f6ac85a88bd9b9ed31fd133119b7702
- https://github.com/jaraco/keyring/commit/cbf509b0386c3063d8b2879ce72d78ac18023f72
- https://github.com/jaraco/keyring/commit/cc1ead78d1e3fab9fa8bb0b4bb334cb82d35db52
- https://bugs.launchpad.net/ubuntu/+source/python-keyring/+bug/1004845
- https://github.com/jaraco/keyring
- https://github.com/pypa/advisory-database/tree/main/vulns/keyring/PYSEC-2012-8.yaml
- http://pypi.python.org/pypi/keyring
- http://www.openwall.com/lists/oss-security/2012/10/31/8
- http://www.ubuntu.com/usn/USN-1634-1
