# [M] WSO2 Carbon directory traversal vulnerability

## Summary
Severity: Medium
Advisory: GHSA-mjww-vqqw-v78q
CVE: CVE-2016-4314
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-mjww-vqqw-v78q
Type: github-advisory

## Affected
- Maven: `org.wso2.carbon.commons:org.wso2.carbon.logging.view.ui` — affected >=0

## Details
Directory traversal vulnerability in the LogViewer Admin Service in WSO2 Carbon 4.4.5 allows remote authenticated administrators to read arbitrary files via a .. (dot dot) in the logFile parameter to downloadgz-ajaxprocessor.jsp.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-4314
- https://github.com/wso2/carbon-commons
- https://github.com/wso2/docs-security/blob/main/en/docs/security-announcements/security-advisories/2016/WSO2-2016-0098.md
- https://web.archive.org/web/20201207110545/http://www.securityfocus.com/archive/1/539200/100/0/threaded
- https://www.exploit-db.com/exploits/40240
- http://hyp3rlinx.altervista.org/advisories/WSO2-CARBON-v4.4.5-LOCAL-FILE-INCLUSION.txt
- http://packetstormsecurity.com/files/138330/WSO2-Carbon-4.4.5-Local-File-Inclusion.html
