# [H] Plone allows anonymous users to reset any users password through the web via Password Reset Tool

## Summary
Severity: High
Advisory: GHSA-5hch-v5pq-x4qp
CVE: CVE-2006-4247
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2022-05-01
Source: https://github.com/advisories/GHSA-5hch-v5pq-x4qp
Type: github-advisory

## Affected
- PyPI: `Plone` — affected >=2.5 <2.5.1

## Details
Unspecified vulnerability in the Password Reset Tool before 0.4.1 on Plone 2.5 and 2.5.1 Release Candidate allows attackers to reset the passwords of other users, related to "an erroneous security declaration."

## References
- https://nvd.nist.gov/vuln/detail/CVE-2006-4247
- https://github.com/plone/Plone
- https://github.com/pypa/advisory-database/tree/main/vulns/plone/PYSEC-2006-5.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/plone/PYSEC-2006-9.yaml
- http://plone.org/about/security/advisories/cve-2006-4247
