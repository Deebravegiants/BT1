# [C] CVE-2019-1010161

## Summary
Severity: Critical
Advisory: CVE-2019-1010161
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-07-25
Source: https://osv.dev/vulnerability/CVE-2019-1010161
Type: osv

## Details
perl-CRYPT-JWT 0.022 and earlier is affected by: Incorrect Access Control. The impact is: bypass authentication. The component is: JWT.pm for JWT security token, line 614 in _decode_jws(). The attack vector is: network connectivity(crafting user-controlled input to bypass authentication). The fixed version is: 0.023.

## References
- https://github.com/DCIT/perl-Crypt-JWT/issues/3#issuecomment-417947483
