# [H] CVE-2018-16789

## Summary
Severity: High
Advisory: CVE-2018-16789
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-03-21
Source: https://osv.dev/vulnerability/CVE-2018-16789
Type: osv

## Details
libhttp/url.c in shellinabox through 2.20 has an implementation flaw in the HTTP request parsing logic. By sending a crafted multipart/form-data HTTP request, an attacker could exploit this to force shellinaboxd into an infinite loop, exhausting available CPU resources and taking the service down.

## References
- https://code.google.com/archive/p/shellinabox/issues
- http://packetstormsecurity.com/files/149978/Shell-In-A-Box-2.2.0-Denial-Of-Service.html
- http://seclists.org/fulldisclosure/2018/Oct/50
- https://github.com/shellinabox/shellinabox/commit/4f0ecc31ac6f985e0dd3f5a52cbfc0e9251f6361
