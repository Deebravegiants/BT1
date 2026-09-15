# [H] CVE-2017-11692

## Summary
Severity: High
Advisory: CVE-2017-11692
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-07-30
Source: https://osv.dev/vulnerability/CVE-2017-11692
Type: osv

## Details
The function "Token& Scanner::peek" in scanner.cpp in yaml-cpp 0.5.3 and earlier allows remote attackers to cause a denial of service (assertion failure and application exit) via a '!2' string.

## References
- https://security.gentoo.org/glsa/202007-14
- https://github.com/jbeder/yaml-cpp/issues/519
