# [C] CVE-2019-17240

## Summary
Severity: Critical
Advisory: CVE-2019-17240
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-10-06
Source: https://osv.dev/vulnerability/CVE-2019-17240
Type: osv

## Details
bl-kernel/security.class.php in Bludit 3.9.2 allows attackers to bypass a brute-force protection mechanism by using many different forged X-Forwarded-For or Client-IP HTTP headers.

## References
- http://packetstormsecurity.com/files/158875/Bludit-3.9.2-Authentication-Bruteforce-Mitigation-Bypass.html
- http://packetstormsecurity.com/files/159664/Bludit-3.9.2-Bruteforce-Mitigation-Bypass.html
- https://github.com/bludit/bludit/pull/1090
- https://rastating.github.io/bludit-brute-force-mitigation-bypass/
