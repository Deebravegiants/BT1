# [M] Alkacon OpenCms Exposes JSP Source Code

## Summary
Severity: Medium
Advisory: GHSA-c5vw-342h-x5rx
CVE: CVE-2006-3936
CWE: CWE-200
Ecosystem: Maven
Published: 2022-05-01
Source: https://github.com/advisories/GHSA-c5vw-342h-x5rx
Type: github-advisory

## Affected
- Maven: `org.opencms:opencms-core` — affected >=0 <6.2.2

## Details
`system/workplace/editors/editor.jsp` in Alkacon OpenCms before 6.2.2 allows remote authenticated users to read the source code of arbitrary JSP files by specifying the file in the resource parameter, as demonstrated using `index.jsp`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2006-3936
- https://exchange.xforce.ibmcloud.com/vulnerabilities/28001
- https://github.com/alkacon/opencms-core
- https://web.archive.org/web/20061014175017/http://o0o.nu/~meder/OpenCMS_multiple_vulnerabilities.txt
- https://web.archive.org/web/20201208142708/http://www.securityfocus.com/archive/1/441182/100/0/threaded
- http://www.opencms.org/opencms/en/shownews.html?id=1002
