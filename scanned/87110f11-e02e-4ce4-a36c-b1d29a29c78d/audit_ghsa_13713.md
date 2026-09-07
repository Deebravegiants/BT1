# [H] Improper Neutralization of Input in Advanced User Interface for Jolt

## Summary
Severity: High
Advisory: GHSA-68pr-6fjc-wmgm
CVE: CVE-2023-49145
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:C/C:H/I:H/A:L (CVSS_V3)
Published: 2023-11-28
Source: https://github.com/advisories/GHSA-68pr-6fjc-wmgm
Type: github-advisory

## Affected
- Maven: `org.apache.nifi:nifi-jolt-transform-json-ui` — affected >=0 <1.24.0

## Details
Apache NiFi 0.7.0 through 1.23.2 include the JoltTransformJSON Processor, which provides an advanced configuration user interface that is vulnerable to DOM-based cross-site scripting. If an authenticated user, who is authorized to configure a JoltTransformJSON Processor, visits a crafted URL, then arbitrary JavaScript code can be executed within the session context of the authenticated user. Upgrading to Apache NiFi 1.24.0 or 2.0.0-M1 is the recommended mitigation.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-49145
- https://github.com/apache/nifi/pull/8060
- https://github.com/apache/nifi/commit/50efc55df6bb00ea15adcc2459d5cc82d128857f
- https://github.com/apache/nifi
- https://issues.apache.org/jira/browse/NIFI-12403
- https://lists.apache.org/thread/j8rd0qsvgoj0khqck5f49jfbp0fm8r1o
- https://nifi.apache.org/security.html#CVE-2023-49145
- http://www.openwall.com/lists/oss-security/2023/11/27/5
