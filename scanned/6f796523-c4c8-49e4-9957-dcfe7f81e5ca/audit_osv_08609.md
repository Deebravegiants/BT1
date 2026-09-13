# [H] CVE-2016-4802

## Summary
Severity: High
Advisory: CVE-2016-4802
Aliases: CURL-CVE-2016-4802
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-06-24
Source: https://osv.dev/vulnerability/CVE-2016-4802
Type: osv

## Details
Multiple untrusted search path vulnerabilities in cURL and libcurl before 7.49.1, when built with SSPI or telnet is enabled, allow local users to execute arbitrary code and conduct DLL hijacking attacks via a Trojan horse (1) security.dll, (2) secur32.dll, or (3) ws2_32.dll in the application or current working directory.

## References
- http://www.securityfocus.com/bid/90997
- http://www.securitytracker.com/id/1036008
- https://curl.haxx.se/docs/adv_20160530.html
