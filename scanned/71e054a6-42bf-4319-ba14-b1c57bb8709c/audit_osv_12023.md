# [H] CVE-2018-1000659

## Summary
Severity: High
Advisory: CVE-2018-1000659
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-09-06
Source: https://osv.dev/vulnerability/CVE-2018-1000659
Type: osv

## Details
LimeSurvey version 3.14.4 and earlier contains a directory traversal in file upload that allows upload of webshell vulnerability in file upload functionality that can result in remote code execution as authenticated user. This attack appear to be exploitable via An authenticated user can upload a specially crafted zip file to get remote code execution. This vulnerability appears to have been fixed in after commit 72a02ebaaf95a80e26127ee7ee2b123cccce05a7 / version 3.14.4.

## References
- https://github.com/LimeSurvey/LimeSurvey/commit/72a02ebaaf95a80e26127ee7ee2b123cccce05a7
