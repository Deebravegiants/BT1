# [C] CVE-2021-21307

## Summary
Severity: Critical
Advisory: CVE-2021-21307
Aliases: GHSA-2xvv-723c-8p7r
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-02-11
Source: https://osv.dev/vulnerability/CVE-2021-21307
Type: osv

## Details
Lucee Server is a dynamic, Java based (JSR-223), tag and scripting language used for rapid web application development. In Lucee Admin before versions 5.3.7.47, 5.3.6.68 or 5.3.5.96 there is an unauthenticated remote code exploit. This is fixed in versions 5.3.7.47, 5.3.6.68 or 5.3.5.96. As a workaround, one can block access to the Lucee Administrator.

## References
- https://dev.lucee.org/t/lucee-vulnerability-alert-november-2020/7643
- https://github.com/lucee/Lucee/security/advisories/GHSA-2xvv-723c-8p7r
- https://portswigger.net/daily-swig/security-researchers-earn-50k-after-exposing-critical-flaw-in-apple-travel-portal
- http://ciacfug.org/blog/updating-lucee-as-part-of-a-vulnerability-alert-response
- https://github.com/lucee/Lucee/commit/6208ab7c44c61d26c79e0b0af10382899f57e1ca
- http://packetstormsecurity.com/files/163864/Lucee-Administrator-imgProcess.cfm-Arbitrary-File-Write.html
- https://github.com/httpvoid/writeups/blob/main/Apple-RCE.md
