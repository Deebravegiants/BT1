# [C] CVE-2018-19586

## Summary
Severity: Critical
Advisory: CVE-2018-19586
CVSS: 9.9 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2019-04-09
Source: https://osv.dev/vulnerability/CVE-2018-19586
Type: osv

## Details
Silverpeas 5.15 through 6.0.2 is affected by an authenticated Directory Traversal vulnerability that can be triggered during file uploads because core/webapi/upload/FileUploadData.java mishandles a StringUtil.java call. This vulnerability enables regular users to write arbitrary files on the underlying system with privileges of the user running the application. Especially, an attacker may leverage the vulnerability to write an executable JSP file in an exposed web directory to execute commands on the underlying system.

## References
- https://github.com/Silverpeas/Silverpeas-Core/blob/d8c3bbb0695a4907db013401bd16c6527e2b4f41/core-web/src/main/java/org/silverpeas/core/webapi/upload/FileUploadData.java#L89
- https://www.bishopfox.com/news/2019/01/silverpeas-5-15-to-6-0-2-path-traversal/
