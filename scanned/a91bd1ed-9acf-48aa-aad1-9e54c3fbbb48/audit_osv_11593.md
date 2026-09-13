# [C] CVE-2017-8911

## Summary
Severity: Critical
Advisory: CVE-2017-8911
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-05-12
Source: https://osv.dev/vulnerability/CVE-2017-8911
Type: osv

## Details
An integer underflow has been identified in the unicode_to_utf8() function in tnef 1.4.14. This might lead to invalid write operations, controlled by an attacker.

## References
- http://www.debian.org/security/2017/dsa-3869
- https://security.gentoo.org/glsa/201708-02
- https://github.com/verdammelt/tnef/issues/23
