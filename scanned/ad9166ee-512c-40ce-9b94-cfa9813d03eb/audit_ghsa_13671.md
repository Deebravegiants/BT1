# [C] SQL injection in Apache Submarine

## Summary
Severity: Critical
Advisory: GHSA-v5gj-fx3g-hcpw
CVE: CVE-2023-37924
CWE: CWE-89
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-11-22
Source: https://github.com/advisories/GHSA-v5gj-fx3g-hcpw
Type: github-advisory

## Affected
- PyPI: `apache-submarine` — affected >=0.7.0 <0.8.0

## Details
Apache Software Foundation Apache Submarine has an SQL injection vulnerability when a user logs in. This issue can result in unauthorized login.

Now we have fixed this issue and now user must have the correct login to access workbench. This issue affects Apache Submarine: from 0.7.0 before 0.8.0. We recommend that all submarine users with 0.7.0 upgrade to 0.8.0, which not only fixes the issue, supports the oidc authentication mode, but also removes the case of unauthenticated logins.

If using the version lower than 0.8.0 and not want to upgrade, you can try cherry-pick PR  https://github.com/apache/submarine/pull/1037 https://github.com/apache/submarine/pull/1054  and rebuild the submarine-server image to fix this.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-37924
- https://github.com/apache/submarine/pull/1037
- https://github.com/apache/submarine/commit/4cd2af10499ac6dc4f82bda179d9f414a522abef
- https://github.com/apache/submarine
- https://github.com/pypa/advisory-database/tree/main/vulns/apache-submarine/PYSEC-2023-244.yaml
- https://issues.apache.org/jira/browse/SUBMARINE-1361
- https://lists.apache.org/thread/g99h773vd49n1wyghdq1llv2f83w1b3r
