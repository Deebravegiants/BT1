# [M] pgAdmin 4 Open Redirect vulnerability

## Summary
Severity: Medium
Advisory: GHSA-894c-rg7f-3c62
CVE: CVE-2023-22298
CWE: CWE-601
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-01-17
Source: https://github.com/advisories/GHSA-894c-rg7f-3c62
Type: github-advisory

## Affected
- PyPI: `pgadmin4` — affected >=0 <6.14

## Details
Open redirect vulnerability in pgAdmin 4 versions prior to v6.14 allows a remote unauthenticated attacker to redirect a user to an arbitrary web site and conduct a phishing attack by having a user to access a specially crafted URL.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-22298
- https://github.com/pgadmin-org/pgadmin4/issues/5343
- https://github.com/pgadmin-org/pgadmin4
- https://jvn.jp/en/jp/JVN03832974/index.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/VHY2B25YHIIFQ3G44TR7NNEST7FJGJPH
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/VHY2B25YHIIFQ3G44TR7NNEST7FJGJPH
- https://www.pgadmin.org
