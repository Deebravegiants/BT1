# [M] Apache Superset vulnerable to Cross-site Scripting

## Summary
Severity: Medium
Advisory: GHSA-9f88-wg5r-947j
CVE: CVE-2022-43717
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-01-16
Source: https://github.com/advisories/GHSA-9f88-wg5r-947j
Type: github-advisory

## Affected
- PyPI: `apache-superset` — affected >=0
- PyPI: `apache-superset` — affected 2.0.0

## Details
Dashboard rendering does not sufficiently sanitize the content of markdown components leading to possible XSS attack vectors that can be performed by authenticated users with create dashboard permissions. This issue affects Apache Superset version 1.5.2 and prior versions and version 2.0.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-43717
- https://github.com/apache/superset
- https://lists.apache.org/thread/g6zy6vkpvkbj5mj32vmyzwol5ldtg9pl
