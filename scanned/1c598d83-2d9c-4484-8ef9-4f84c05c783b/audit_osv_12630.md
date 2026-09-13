# [C] CVE-2018-13818

## Summary
Severity: Critical
Advisory: CVE-2018-13818
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-07-10
Source: https://osv.dev/vulnerability/CVE-2018-13818
Type: osv

## Details
Twig before 2.4.4 allows Server-Side Template Injection (SSTI) via the search search_key parameter. NOTE: the vendor points out that Twig itself is not a web application and states that it is the responsibility of web applications using Twig to properly wrap input to it

## References
- https://github.com/twigphp/Twig/blob/2.x/CHANGELOG
- https://github.com/twigphp/Twig/commit/eddb97148ad779f27e670e1e3f19fb323aedafeb
- https://github.com/twigphp/Twig/issues/2743
- https://mobile.twitter.com/jameel_nabbo/status/1032593354704515072?s=20
- https://www.exploit-db.com/exploits/44102/
