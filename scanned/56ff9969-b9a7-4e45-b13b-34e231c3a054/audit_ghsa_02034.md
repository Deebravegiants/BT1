# [H] Shell command injection in Apache Syncope

## Summary
Severity: High
Advisory: GHSA-p2rp-cmjq-r7wm
CVE: CVE-2020-11977
CWE: CWE-78
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-06-16
Source: https://github.com/advisories/GHSA-p2rp-cmjq-r7wm
Type: github-advisory

## Affected
- Maven: `org.apache.syncope:syncope` — affected >=2.1.0 <2.1.7

## Details
In Apache Syncope 2.1.X releases prior to 2.1.7, when the Flowable extension is enabled, an administrator with workflow entitlements can use Shell Service Tasks to perform malicious operations, including but not limited to file read, file write, and code execution.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-11977
- https://syncope.apache.org/security#CVE-2020-11977:_Remote_Code_Execution_via_Flowable_workflow_definition
