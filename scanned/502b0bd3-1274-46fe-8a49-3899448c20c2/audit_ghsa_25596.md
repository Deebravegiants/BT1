# [H] JBoss AS may expose root content if excluded-contexts list is mismatched

## Summary
Severity: High
Advisory: GHSA-wq8g-hm94-5rqq
CVE: CVE-2012-1094
CWE: CWE-200
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-04-23
Source: https://github.com/advisories/GHSA-wq8g-hm94-5rqq
Type: github-advisory

## Affected
- Maven: `org.jboss.as:jboss-as-server` — affected >=7.0.0.Alpha1 <7.1.1.Final

## Details
JBoss AS 7 prior to 7.1.1 and mod_cluster do not handle default hostname in the same way, which can cause the excluded-contexts list to be mismatched and the root context to be exposed.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2012-1094
- https://access.redhat.com/security/cve/cve-2012-1094
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2012-1094
