# [H] CVE-2014-0242

## Summary
Severity: High
Advisory: CVE-2014-0242
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-12-09
Source: https://osv.dev/vulnerability/CVE-2014-0242
Type: osv

## Details
mod_wsgi module before 3.4 for Apache, when used in embedded mode, might allow remote attackers to obtain sensitive information via the Content-Type header which is generated from memory that may have been freed and then overwritten by a separate thread.

## References
- http://blog.dscpl.com.au/2014/05/security-release-for-modwsgi-version-35.html
- http://modwsgi.readthedocs.org/en/latest/release-notes/version-3.4.html
- http://www.securityfocus.com/bid/67534
- http://www.openwall.com/lists/oss-security/2014/05/21/1
