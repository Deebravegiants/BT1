# [C] CVE-2019-1010263

## Summary
Severity: Critical
Advisory: CVE-2019-1010263
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-07-17
Source: https://osv.dev/vulnerability/CVE-2019-1010263
Type: osv

## Details
Perl Crypt::JWT prior to 0.023 is affected by: Incorrect Access Control. The impact is: allow attackers to bypass authentication by providing a token by crafting with hmac(). The component is: JWT.pm, line 614. The attack vector is: network connectivity. The fixed version is: after commit b98a59b42ded9f9e51b2560410106207c2152d6c.

## References
- https://github.com/DCIT/perl-Crypt-JWT/commit/b98a59b42ded9f9e51b2560410106207c2152d6c
- https://www.openwall.com/lists/oss-security/2018/09/07/1
