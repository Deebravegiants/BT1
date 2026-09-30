# [H] CVE-2018-8764

## Summary
Severity: High
Advisory: CVE-2018-8764
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-03-27
Source: https://osv.dev/vulnerability/CVE-2018-8764
Type: osv

## Details
Roland Gruber Softwareentwicklung LDAP Account Manager before 6.3 places a CSRF token in the sec_token parameter of a URI, which makes it easier for remote attackers to defeat a CSRF protection mechanism by leveraging logging.

## References
- https://www.debian.org/security/2018/dsa-4165
- http://packetstormsecurity.com/files/146858/LDAP-Account-Manager-6.2-Cross-Site-Scripting.html
- http://seclists.org/fulldisclosure/2018/Mar/45
