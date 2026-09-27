# [H] CVE-2017-11466

## Summary
Severity: High
Advisory: CVE-2017-11466
CVSS: 7.2 (CVSS:3.0/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-07-20
Source: https://osv.dev/vulnerability/CVE-2017-11466
Type: osv

## Details
Arbitrary file upload vulnerability in com/dotmarketing/servlets/AjaxFileUploadServlet.class in dotCMS 4.1.1 allows remote authenticated administrators to upload .jsp files to arbitrary locations via directory traversal sequences in the fieldName parameter to servlets/ajax_file_upload. This results in arbitrary code execution by requesting the .jsp file at a /assets URI.

## References
- https://github.com/dotCMS/core/issues/12131
- http://seclists.org/fulldisclosure/2017/Jul/33
- https://packetstormsecurity.com/files/143383/dotcms411-shell.txt
