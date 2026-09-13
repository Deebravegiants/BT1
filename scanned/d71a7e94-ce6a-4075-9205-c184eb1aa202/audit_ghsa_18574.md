# [M] Apache Struts Extras Before 2 has an Improper Output Neutralization for Logs Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-cx25-xg7c-xfm5
CVE: CVE-2025-54656
CWE: CWE-117
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2025-07-30
Source: https://github.com/advisories/GHSA-cx25-xg7c-xfm5
Type: github-advisory

## Affected
- Maven: `org.apache.struts:struts-extras` — affected >=0
- Maven: `struts:struts` — affected 1.2.9

## Details
** UNSUPPORTED WHEN ASSIGNED ** Improper Output Neutralization for Logs vulnerability in Apache Struts.

This issue affects Apache Struts Extras: before 2.

When using LookupDispatchAction, in some cases, Struts may print untrusted input to the logs without any filtering. Specially-crafted input may lead to log output where part of the message masquerades as a separate log line, confusing consumers of the logs (either human or automated). 

As this project is retired, we do not plan to release a version that fixes this issue. Users are recommended to find an alternative or restrict access to the instance to trusted users.

NOTE: This vulnerability only affects products that are no longer supported by the maintainer.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-54656
- https://github.com/apache/struts
- https://lists.apache.org/thread/so5cn07j2zn9vlf1xnfqp630wts719rr
- http://www.openwall.com/lists/oss-security/2025/07/30/1
