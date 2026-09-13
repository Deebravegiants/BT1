# [H] CVE-2016-3735

## Summary
Severity: High
Advisory: CVE-2016-3735
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-01-28
Source: https://osv.dev/vulnerability/CVE-2016-3735
Type: osv

## Details
Piwigo is image gallery software written in PHP. When a criteria is not met on a host, piwigo defaults to usingmt_rand in order to generate password reset tokens. mt_rand output can be predicted after recovering the seed used to generate it. This low an unauthenticated attacker to take over an account providing they know an administrators email address in order to be able to request password reset.

## References
- http://piwigo.org/release-2.8.1%2C
- https://github.com/Piwigo/Piwigo/issues/470%2C
- https://github.com/Piwigo/Piwigo/commit/f51ee90c66527fd7ff634f3e8d414cb670da068d
