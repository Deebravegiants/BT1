# [H] Total.js CMS Path Traversal

## Summary
Severity: High
Advisory: GHSA-pwvp-h579-hfxg
CVE: CVE-2019-15952
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-pwvp-h579-hfxg
Type: github-advisory

## Affected
- npm: `total4` — affected 12.0

## Details
An issue was discovered in Total.js CMS 12.0.0. An authenticated user with the Pages privilege can conduct a path traversal attack (../) to include .html files that are outside the permitted directory. Also, if a page contains a template directive, then the directive will be server side processed. Thus, if a user can control the content of a .html file, then they can inject a payload with a malicious template directive to gain Remote Command Execution. The exploit will work only with the .html extension.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-15952
- https://github.com/beerpwn/CVE/blob/master/Totaljs_disclosure_report/report_final.pdf
- https://github.com/totaljs/cms
- https://seclists.org/fulldisclosure/2019/Sep/2
