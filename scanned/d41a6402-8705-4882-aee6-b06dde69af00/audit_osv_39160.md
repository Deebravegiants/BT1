# [C] efw4.X: RCE via zipslip

## Summary
Severity: Critical
Advisory: CVE-2026-44257
Aliases: GHSA-q7jx-7x5r-r9f6
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-05-12
Source: https://osv.dev/vulnerability/CVE-2026-44257
Type: osv

## Details
efw4.X is an Enterprise Framework for Web. Prior to 4.08.010, efw.file.FileManager.unZip writes zip entries to disk using new File(baseDir, zipEntry.getName()) with no canonical-path check. An entry name such as ../../../pwned.jsp escapes the intended extraction directory and lands anywhere the Tomcat process can write — including the servlet context root. Combined with the framework's multipart /uploadServlet and an event that calls file.saveUploadFiles + FileManager.unZip, a remote attacker with no credentials drops a JSP webshell and executes arbitrary commands as the Tomcat user. This vulnerability is fixed in 4.08.010.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/44xxx/CVE-2026-44257.json
- https://github.com/efwGrp/efw4.X/security/advisories/GHSA-q7jx-7x5r-r9f6
- https://nvd.nist.gov/vuln/detail/CVE-2026-44257
