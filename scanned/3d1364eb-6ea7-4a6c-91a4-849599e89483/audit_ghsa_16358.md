# [H] Python Cryptography package vulnerable to Bleichenbacher timing oracle attack

## Summary
Severity: High
Advisory: GHSA-3ww4-gg4f-jr7f
CVE: CVE-2023-50782
CWE: CWE-203, CWE-208, CWE-385
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-02-05
Source: https://github.com/advisories/GHSA-3ww4-gg4f-jr7f
Type: github-advisory

## Affected
- PyPI: `cryptography` — affected >=0 <42.0.0

## Details
A flaw was found in the python-cryptography package. This issue may allow a remote attacker to decrypt captured messages in TLS servers that use RSA key exchanges, which may lead to exposure of confidential or sensitive data.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-50782
- https://github.com/pyca/cryptography/issues/9785
- https://access.redhat.com/security/cve/CVE-2023-50782
- https://bugzilla.redhat.com/show_bug.cgi?id=2254432
- https://github.com/pyca/cryptography
- https://www.couchbase.com/alerts
