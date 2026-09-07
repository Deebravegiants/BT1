# [M] Cross-site Scripting in Apache DeltaSpike

## Summary
Severity: Medium
Advisory: GHSA-4q23-g7mf-xp98
CVE: CVE-2017-17837
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-4q23-g7mf-xp98
Type: github-advisory

## Affected
- Maven: `org.apache.deltaspike.modules:jsf-module-project` — affected >=0 <1.8.1

## Details
The Apache DeltaSpike-JSF 1.8.0 module has a XSS injection leak in the windowId handling. The default size of the windowId get's cut off after 10 characters (by default), so the impact might be limited. A fix got applied and released in Apache deltaspike-1.8.1.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-17837
- https://github.com/apache/deltaspike/commit/4e2502358526b944fc5514c206d306e97ff271bb
- https://git-wip-us.apache.org/repos/asf?p=deltaspike.git;h=4e25023
- https://issues.apache.org/jira/browse/DELTASPIKE-1307
- https://lists.apache.org/thread.html/r17b326c0eb35d8c71c84c171eda83e3e1f011dc757781e34f2846018@%3Cdev.deltaspike.apache.org%3E
- https://lists.apache.org/thread.html/r78565f0f4ecb4ad32a6c405b45b9ee568dfc4729ba63e7d7cb6adf88@%3Cdev.deltaspike.apache.org%3E
