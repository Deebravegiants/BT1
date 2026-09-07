# [M] pgAdmin is affected by a multi-factor authentication bypass vulnerability

## Summary
Severity: Medium
Advisory: GHSA-2mvc-557g-5638
CVE: CVE-2024-4215
CWE: CWE-89
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:L/A:L (CVSS_V3)
Published: 2024-05-02
Source: https://github.com/advisories/GHSA-2mvc-557g-5638
Type: github-advisory

## Affected
- PyPI: `pgadmin4` — affected >=0 <8.6

## Details
pgAdmin <= 8.5 is affected by a multi-factor authentication bypass vulnerability. This vulnerability allows an attacker with knowledge of a legitimate account’s username and password may authenticate to the application and perform sensitive actions within the application, such as managing files and executing SQL queries, regardless of the account’s MFA enrollment status.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-4215
- https://github.com/pgadmin-org/pgadmin4/issues/7425
- https://github.com/pgadmin-org/pgadmin4/commit/f4761f55f7cf6d56d6c5129f921393b0b47fd976
- https://github.com/pgadmin-org/pgadmin4
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/T2YFVCB4HCXU3FQBZ5XTWJZWSZUDNCXE
