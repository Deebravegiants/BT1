# [M] CVE-2018-6191

## Summary
Severity: Medium
Advisory: CVE-2018-6191
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-01-24
Source: https://osv.dev/vulnerability/CVE-2018-6191
Type: osv

## Details
The js_strtod function in jsdtoa.c in Artifex MuJS through 1.0.2 has an integer overflow because of incorrect exponent validation.

## References
- http://git.ghostscript.com/?p=mujs.git%3Ba=commit%3Bh=25821e6d74fab5fcc200fe5e818362e03e114428
- http://www.securityfocus.com/bid/102840
- https://bugs.ghostscript.com/show_bug.cgi?id=698920
- https://www.exploit-db.com/exploits/43903/
