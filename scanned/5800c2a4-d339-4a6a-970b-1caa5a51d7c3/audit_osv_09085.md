# [C] CVE-2016-7791

## Summary
Severity: Critical
Advisory: CVE-2016-7791
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-01-12
Source: https://osv.dev/vulnerability/CVE-2016-7791
Type: osv

## Details
Exponent CMS 2.3.9 suffers from a remote code execution vulnerability in /install/index.php. An attacker can upload an evil 'exploit.tar.gz' file to the website, then extract it by visiting '/install/index.php?install_sample=../../files/exploit', which leads to arbitrary code execution.

## References
- http://www.securityfocus.com/bid/93119
- http://www.openwall.com/lists/oss-security/2016/09/29/11
