# [M] CVE-2020-8866

## Summary
Severity: Medium
Advisory: CVE-2020-8866
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2020-03-23
Source: https://osv.dev/vulnerability/CVE-2020-8866
Type: osv

## Details
This vulnerability allows remote attackers to create arbitrary files on affected installations of Horde Groupware Webmail Edition 5.2.22. Authentication is required to exploit this vulnerability. The specific flaw exists within add.php. The issue results from the lack of proper validation of user-supplied data, which can allow the upload of arbitrary files. An attacker can leverage this in conjunction with other vulnerabilities to execute code in the context of the www-data user. Was ZDI-CAN-10125.

## References
- https://lists.debian.org/debian-lts-announce/2020/03/msg00036.html
- https://lists.horde.org/archives/announce/2020/001288.html
- https://www.zerodayinitiative.com/advisories/ZDI-20-275/
