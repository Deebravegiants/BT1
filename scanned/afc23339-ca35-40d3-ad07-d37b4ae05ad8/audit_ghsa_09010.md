# [M] Apache Commons Configuration: StackOverflowError for YAML input with cycles

## Summary
Severity: Medium
Advisory: GHSA-337m-mw94-2v6g
CVE: CVE-2026-45205
CWE: CWE-674
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-05-14
Source: https://github.com/advisories/GHSA-337m-mw94-2v6g
Type: github-advisory

## Affected
- Maven: `org.apache.commons:commons-configuration2` — affected >=2.2 <2.15.0

## Details
Uncontrolled Recursion vulnerability in Apache Commons.

When processing an untrusted configuration file, Commons Configuration will throw a StackOverflowError for YAML input with cycles.
This issue affects Apache Commons: from 2.2 before 2.15.0.

Users are recommended to upgrade to version 2.15.0, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-45205
- https://github.com/apache/commons-configuration/pull/634
- https://github.com/apache/commons-configuration
- https://lists.apache.org/thread/q3q3j10ohcqhs6o0rg1v7kz6kk27vtkk
- http://www.openwall.com/lists/oss-security/2026/05/14/5
