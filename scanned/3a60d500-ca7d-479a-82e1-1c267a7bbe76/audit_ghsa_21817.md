# [H] Incorrect Default Permissions in Apache DolphinScheduler

## Summary
Severity: High
Advisory: GHSA-qhh5-9738-g9mx
CVE: CVE-2020-13922
CWE: CWE-276
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-02-09
Source: https://github.com/advisories/GHSA-qhh5-9738-g9mx
Type: github-advisory

## Affected
- Maven: `org.apache.dolphinscheduler:dolphinscheduler-api` — affected >=0 <1.3.2

## Details
Versions of Apache DolphinScheduler prior to 1.3.2 allowed an ordinary user under any tenant to override another users password through the API interface.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-13922
- https://github.com/apache/incubator-dolphinscheduler/commit/b8a9e2e00f2f207ae60c913a7173b59405ff95f1
- https://github.com/apache/incubator-dolphinscheduler
- https://github.com/pypa/advisory-database/tree/main/vulns/apache-dolphinscheduler/PYSEC-2021-876.yaml
- https://www.mail-archive.com/announce%40apache.org/msg06076.html
- https://www.mail-archive.com/announce@apache.org/msg06076.html
