# [H] Apache superset missing check for default SECRET_KEY

## Summary
Severity: High
Advisory: GHSA-5cx2-vq3h-x52c
CVE: CVE-2023-27524
CWE: CWE-1188
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:L/E:H (CVSS_V3)
Published: 2023-04-24
Source: https://github.com/advisories/GHSA-5cx2-vq3h-x52c
Type: github-advisory

## Affected
- PyPI: `apache-superset` — affected >=0 <2.1.0

## Details
Session Validation attacks in Apache Superset versions up to and including 2.0.1. Installations that have not altered the default configured SECRET_KEY according to installation instructions allow for an attacker to authenticate and access unauthorized resources. This does not affect Superset administrators who have changed the default value for SECRET_KEY config.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-27524
- https://github.com/apache/superset/commit/b180319bbf08e876ea84963220ebebbfd0699e03
- https://github.com/apache/superset
- https://lists.apache.org/thread/n0ftx60sllf527j7g11kmt24wvof8xyk
- https://packetstormsecurity.com/files/172522/Apache-Superset-2.0.0-Authentication-Bypass.html
- https://packetstormsecurity.com/files/175094/Apache-Superset-2.0.0-Remote-Code-Execution.html
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2023-27524
- https://www.openwall.com/lists/oss-security/2023/04/24/2
- http://www.openwall.com/lists/oss-security/2023/04/24/2
