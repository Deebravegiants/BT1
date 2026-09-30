# [H] PyCA Cryptography vulnerable to GCM tag forgery

## Summary
Severity: High
Advisory: GHSA-fcf9-3qw3-gxmj
CVE: CVE-2018-10903
CWE: CWE-20
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2018-07-31
Source: https://github.com/advisories/GHSA-fcf9-3qw3-gxmj
Type: github-advisory

## Affected
- PyPI: `cryptography` — affected >=1.9.0 <2.3

## Details
A flaw was found in python-cryptography versions between >=1.9.0 and <2.3. The finalize_with_tag API did not enforce a minimum tag length. If a user did not validate the input length prior to passing it to finalize_with_tag an attacker could craft an invalid payload with a shortened tag (e.g. 1 byte) such that they would have a 1 in 256 chance of passing the MAC check. GCM tag forgeries can cause key leakage.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-10903
- https://github.com/pyca/cryptography/pull/4342
- https://github.com/pyca/cryptography/commit/d4378e42937b56f473ddade2667f919ce32208cb
- https://access.redhat.com/errata/RHSA-2018:3600
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-10903
- https://github.com/advisories/GHSA-fcf9-3qw3-gxmj
- https://github.com/pyca/cryptography
- https://github.com/pypa/advisory-database/tree/main/vulns/cryptography/PYSEC-2018-52.yaml
- https://usn.ubuntu.com/3720-1
