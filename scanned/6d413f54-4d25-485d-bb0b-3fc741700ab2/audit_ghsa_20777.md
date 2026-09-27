# [H] rdiffweb vulnerable to Sensitive Cookie in HTTPS Session Without 'Secure' Attribute

## Summary
Severity: High
Advisory: GHSA-mjw4-xvx6-3grg
CVE: CVE-2022-3174
CWE: CWE-311, CWE-614
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-09-14
Source: https://github.com/advisories/GHSA-mjw4-xvx6-3grg
Type: github-advisory

## Affected
- PyPI: `rdiffweb` — affected >=2.4.1 <2.4.2

## Details
rdiffweb version 2.4.1 is vulnerable to Sensitive Cookie in HTTPS Session Without 'Secure' Attribute. This makes it so that a user's cookies can be sent to the server with an unencrypted request over the HTTP protocol. Version 2.4.2 contains a fix for the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-3174
- https://github.com/ikus060/rdiffweb/commit/f2de2371c5e13ce1c6fd6f9a1ed3e5d46b93cd7e
- https://github.com/advisories/GHSA-mjw4-xvx6-3grg
- https://github.com/ikus060/rdiffweb
- https://github.com/pypa/advisory-database/tree/main/vulns/rdiffweb/PYSEC-2022-271.yaml
- https://huntr.dev/bounties/d8a32bd6-c76d-4140-a5ca-ef368a3058ce
