# [H] CVE-2017-15644

## Summary
Severity: High
Advisory: CVE-2017-15644
CVSS: 8.6 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N)
Published: 2017-10-19
Source: https://osv.dev/vulnerability/CVE-2017-15644
Type: osv

## Details
SSRF exists in Webmin 1.850 via the PATH_INFO to tunnel/link.cgi, as demonstrated by a GET request for tunnel/link.cgi/http://INTRANET-IP:8000.

## References
- http://www.webmin.com/changes.html
- http://www.webmin.com/security.html
- https://github.com/webmin/webmin/commit/0c58892732ee7610a7abba5507614366d382c9c9
- https://blogs.securiteam.com/index.php/archives/3430
