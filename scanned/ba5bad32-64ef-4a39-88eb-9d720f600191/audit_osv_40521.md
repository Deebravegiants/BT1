# [C] Apache Syncope: Remote Code Execution via Flowable BPMN Groovy ScriptTask

## Summary
Severity: Critical
Advisory: CVE-2026-53405
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-20
Source: https://osv.dev/vulnerability/CVE-2026-53405
Type: osv

## Details
Improper Isolation or Compartmentalization vulnerability in Apache Syncope.

An administrator with adequate entitlements can import arbitrary BPMN process definitions via the REST API and then start the process. When a BPMN process containing a Groovy scriptTask is imported and started, the Groovy script is executed directly on the server, with no sandbox.


This issue affects Apache Syncope: from 3.0.0-M0 through 3.0.16, from 4.0.0-M0 Through 4.0.6, from 4.1.0-M0 through 4.1.1.




Users are recommended to upgrade to version 4.0.7 / 4.1.2, which fix this issue by wrapping Flowable's Groovy scriptTasks with security sandbox.

## References
- http://www.openwall.com/lists/oss-security/2026/07/20/6
- https://repo.maven.apache.org/maven2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53405.json
- https://lists.apache.org/thread/vdq0tk6ylffz6trbgbllj9kb1ndzff7k
- https://nvd.nist.gov/vuln/detail/CVE-2026-53405
