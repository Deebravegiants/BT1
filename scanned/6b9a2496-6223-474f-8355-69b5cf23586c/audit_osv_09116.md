# [M] CVE-2016-7965

## Summary
Severity: Medium
Advisory: CVE-2016-7965
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N)
Published: 2016-10-31
Source: https://osv.dev/vulnerability/CVE-2016-7965
Type: osv

## Details
DokuWiki 2016-06-26a and older uses $_SERVER[HTTP_HOST] instead of the baseurl setting as part of the password-reset URL. This can lead to phishing attacks. (A remote unauthenticated attacker can change the URL's hostname via the HTTP Host header.) The vulnerability can be triggered only if the Host header is not part of the web server routing process (e.g., if several domains are served by the same web server).

## References
- http://www.securityfocus.com/bid/94237
- https://github.com/splitbrain/dokuwiki/issues/1709
