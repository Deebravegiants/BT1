# [H] SQL injection in Apache DolphinScheduler 

## Summary
Severity: High
Advisory: GHSA-93g4-3phc-g4xw
CVE: CVE-2021-27644
CWE: CWE-89
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-11-03
Source: https://github.com/advisories/GHSA-93g4-3phc-g4xw
Type: github-advisory

## Affected
- Maven: `org.apache.dolphinscheduler:dolphinscheduler-server` — affected >=0 <1.3.6

## Details
In Apache DolphinScheduler before 1.3.6 versions, authorized users can use SQL injection in the data source center. (Only applicable to MySQL data source with internal login account password)

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-27644
- https://lists.apache.org/thread.html/r35d6acf021486a390a7ea09e6650c2fe19e72522bd484791d606a6e6%40%3Cdev.dolphinscheduler.apache.org%3E
- https://lists.apache.org/thread.html/r35d6acf021486a390a7ea09e6650c2fe19e72522bd484791d606a6e6@%3Cdev.dolphinscheduler.apache.org%3E
- http://www.openwall.com/lists/oss-security/2021/11/01/3
