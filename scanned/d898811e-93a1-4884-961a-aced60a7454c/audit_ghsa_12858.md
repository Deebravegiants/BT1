# [C] Apache DolphinScheduler vulnerable to Improper Input Validation

## Summary
Severity: Critical
Advisory: GHSA-3xh5-8hvq-rc8x
CVE: CVE-2022-45875
CWE: CWE-20
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-01-04
Source: https://github.com/advisories/GHSA-3xh5-8hvq-rc8x
Type: github-advisory

## Affected
- Maven: `org.apache.dolphinscheduler:dolphinscheduler` — affected >=0 <3.0.2
- Maven: `org.apache.dolphinscheduler:dolphinscheduler` — affected >=3.1.0 <3.1.1

## Details
Apache DolphinScheduler improperly validates script alert plugin parameters and is vulnerable to remote command execution. This issue affects Apache DolphinScheduler version 3.0.1 and prior versions; version 3.1.0 and prior versions. Users should upgrade to version 3.0.2 or 3.1.1.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-45875
- https://github.com/apache/dolphinscheduler
- https://github.com/pypa/advisory-database/tree/main/vulns/apache-dolphinscheduler/PYSEC-2023-4.yaml
- https://lists.apache.org/thread/r0wqzkjsoq17j6ww381kmpx3jjp9hb6r
- http://www.openwall.com/lists/oss-security/2023/11/22/2
