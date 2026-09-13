# [C] Total.js CMS RCE Vulnerability

## Summary
Severity: Critical
Advisory: GHSA-v287-9w3v-x5c5
CVE: CVE-2019-15954
CWE: CWE-77, CWE-862
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-v287-9w3v-x5c5
Type: github-advisory

## Affected
- npm: `total4` — affected 12.0.0

## Details
An issue was discovered in Total.js CMS 12.0.0. An authenticated user with the widgets privilege can gain achieve Remote Command Execution (RCE) on the remote server by creating a malicious widget with a special tag containing JavaScript code that will be evaluated server side. In the process of evaluating the tag by the back-end, it is possible to escape the sandbox object by using the following payload: `<script total>global.process.mainModule.require(child_process).exec(RCE);</script>`

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-15954
- https://github.com/beerpwn/CVE/blob/master/Totaljs_disclosure_report/report_final.pdf
- https://github.com/totaljs/cms
- https://seclists.org/fulldisclosure/2019/Sep/5
- http://packetstormsecurity.com/files/154924/Total.js-CMS-12-Widget-JavaScript-Code-Injection.html
