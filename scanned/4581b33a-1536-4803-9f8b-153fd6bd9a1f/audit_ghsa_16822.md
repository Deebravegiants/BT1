# [H] Centreon updateLCARelation SQL Injection Remote Code Execution Vulnerability

## Summary
Severity: High
Advisory: GHSA-j4pc-vqvc-4p9x
CVE: CVE-2024-23116
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-04-02
Source: https://github.com/advisories/GHSA-j4pc-vqvc-4p9x
Type: github-advisory

## Affected
- Packagist: `centreon/centreon` — affected >=0 <22.10.15

## Details
Centreon updateLCARelation SQL Injection Remote Code Execution Vulnerability. This vulnerability allows remote attackers to execute arbitrary code on affected installations of Centreon. Authentication is required to exploit this vulnerability.

The specific flaw exists within the updateLCARelation function. The issue results from the lack of proper validation of a user-supplied string before using it to construct SQL queries. An attacker can leverage this vulnerability to execute code in the context of the service account. Was ZDI-CAN-22296.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-23116
- https://github.com/centreon/centreon/pull/2464
- https://github.com/centreon/centreon/commit/c6ee0f67544a70524539b26e8ea92209676a5399
- https://github.com/centreon/centreon
- https://www.zerodayinitiative.com/advisories/ZDI-24-116
