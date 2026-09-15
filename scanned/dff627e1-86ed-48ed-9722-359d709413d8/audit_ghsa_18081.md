# [M] Apache Superset has bypass of `DISALLOWED_SQL_FUNCTIONS` that allows execution of blocked SQL functions

## Summary
Severity: Medium
Advisory: GHSA-fxgf-3xh6-m2pp
CVE: CVE-2025-55674
CWE: CWE-89
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-08-14
Source: https://github.com/advisories/GHSA-fxgf-3xh6-m2pp
Type: github-advisory

## Affected
- PyPI: `apache-superset` — affected >=0 <5.0.0

## Details
A bypass of the DISALLOWED_SQL_FUNCTIONS security feature in Apache Superset allows for the execution of blocked SQL functions. An attacker can use a special inline block to circumvent the denylist. This allows a user with SQL Lab access to execute functions that were intended to be disabled, leading to the disclosure of sensitive database information like the software version.

This issue affects Apache Superset: before 5.0.0.

Users are recommended to upgrade to version 5.0.0, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-55674
- https://github.com/apache/superset
- https://lists.apache.org/thread/cn49ps15ny3g2b1qzdg5mj7hp47p5jdo
- http://www.openwall.com/lists/oss-security/2025/08/14/5
