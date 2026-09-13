# [M] Apache DolphinScheduler's python gateway suffered from improper authentication

## Summary
Severity: Medium
Advisory: GHSA-3jxw-cv35-2mmv
CVE: CVE-2023-25601
CWE: CWE-287
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2023-04-20
Source: https://github.com/advisories/GHSA-3jxw-cv35-2mmv
Type: github-advisory

## Affected
- Maven: `org.apache.dolphinscheduler:dolphinscheduler-api` — affected >=3.0.0 <3.1.2

## Details
On version 3.0.0 through 3.1.1, Apache DolphinScheduler's python gateway suffered from improper authentication: an attacker could use a socket bytes attack without authentication. This issue has been fixed from version 3.1.2 onwards. For users who use version 3.0.0 to 3.1.1, you can turn off the python-gateway function by changing the value `python-gateway.enabled=false` in configuration file `application.yaml`. If you are using the python gateway, please upgrade to version 3.1.2 or above.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-25601
- https://github.com/apache/dolphinscheduler/pull/12893
- https://github.com/apache/dolphinscheduler
- https://github.com/apache/dolphinscheduler/releases/tag/3.1.2
- https://lists.apache.org/thread/25g77jqczp3t8cz56hk1p65q7m6c64rf
- http://www.openwall.com/lists/oss-security/2023/04/20/10
