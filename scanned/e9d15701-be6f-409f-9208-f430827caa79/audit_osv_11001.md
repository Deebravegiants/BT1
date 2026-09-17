# [M] CVE-2017-5595

## Summary
Severity: Medium
Advisory: CVE-2017-5595
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2017-02-06
Source: https://osv.dev/vulnerability/CVE-2017-5595
Type: osv

## Details
A file disclosure and inclusion vulnerability exists in web/views/file.php in ZoneMinder 1.x through v1.30.0 because of unfiltered user-input being passed to readfile(), which allows an authenticated attacker to read local system files (e.g., /etc/passwd) in the context of the web server user (www-data). The attack vector is a .. (dot dot) in the path parameter within a zm/index.php?view=file&path= request.

## References
- http://www.securityfocus.com/bid/96125
- http://seclists.org/bugtraq/2017/Feb/6
- http://seclists.org/fulldisclosure/2017/Feb/11
- https://github.com/ZoneMinder/ZoneMinder/commit/8b19fca9927cdec07cc9dd09bdcf2496a5ae69b3
