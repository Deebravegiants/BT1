# [H] OpenStack Keystone allows /v3/ec2tokens or /v3/s3tokens request with valid AWS Signature to provide Keystone authorization.

## Summary
Severity: High
Advisory: GHSA-hcqg-5g63-7j9h
CVE: CVE-2025-65073
CWE: CWE-863
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:L/I:H/A:N (CVSS_V3)
Published: 2025-11-17
Source: https://github.com/advisories/GHSA-hcqg-5g63-7j9h
Type: github-advisory

## Affected
- PyPI: `keystone` — affected >=0 <26.0.1
- PyPI: `keystone` — affected >=27.0.0.0rc1 <27.0.0
- PyPI: `keystone` — affected >=28.0.0.0rc1 <28.0.0

## Details
OpenStack Keystone before 26.0.1, 27.0.0, and 28.0.0 allows a /v3/ec2tokens or /v3/s3tokens request with a valid AWS Signature to provide Keystone authorization.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-65073
- https://github.com/openstack/keystone
- https://www.openwall.com/lists/oss-security/2025/11/04/2
- http://www.openwall.com/lists/oss-security/2025/11/17/6
