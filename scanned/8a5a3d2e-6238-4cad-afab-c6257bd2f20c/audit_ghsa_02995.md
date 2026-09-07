# [H] Improper Input Validation in pip

## Summary
Severity: High
Advisory: GHSA-5xp3-jfq3-5q8x
CVE: CVE-2021-3572
CWE: CWE-20
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2021-11-15
Source: https://github.com/advisories/GHSA-5xp3-jfq3-5q8x
Type: github-advisory

## Affected
- PyPI: `pip` — affected >=0 <21.1

## Details
A flaw was found in python-pip in the way it handled Unicode separators in git references. A remote attacker could possibly use this issue to install a different revision on a repository. The highest threat from this vulnerability is to data integrity. This is fixed in python-pip version 21.1.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-3572
- https://github.com/pypa/pip/pull/9827
- https://github.com/pypa/pip/commit/e46bdda9711392fec0c45c1175bae6db847cb30b
- https://access.redhat.com/errata/RHSA-2021:3254
- https://bugzilla.redhat.com/show_bug.cgi?id=1962856
- https://github.com/advisories/GHSA-5xp3-jfq3-5q8x
- https://github.com/pypa/advisory-database/tree/main/vulns/pip/PYSEC-2021-437.yaml
- https://github.com/pypa/pip
- https://packetstormsecurity.com/files/162712/USN-4961-1.txt
- https://security.netapp.com/advisory/ntap-20240621-0006
- https://www.oracle.com/security-alerts/cpuapr2022.html
- https://www.oracle.com/security-alerts/cpujul2022.html
