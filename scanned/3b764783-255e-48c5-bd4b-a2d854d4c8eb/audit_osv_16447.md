# [C] CVE-2019-6991

## Summary
Severity: Critical
Advisory: CVE-2019-6991
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-01-28
Source: https://osv.dev/vulnerability/CVE-2019-6991
Type: osv

## Details
A classic Stack-based buffer overflow exists in the zmLoadUser() function in zm_user.cpp of the zmu binary in ZoneMinder through 1.32.3, allowing an unauthenticated attacker to execute code via a long username.

## References
- https://github.com/ZoneMinder/zoneminder/issues/2478
- https://github.com/ZoneMinder/zoneminder/pull/2482
