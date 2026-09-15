# [C] CVE-2017-1000423

## Summary
Severity: Critical
Advisory: CVE-2017-1000423
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-01-02
Source: https://osv.dev/vulnerability/CVE-2017-1000423
Type: osv

## Details
b2evolution version 6.6.0 - 6.8.10 is vulnerable to input validation (backslash and single quote escape) in basic install functionality resulting in unauthenticated attacker gaining PHP code execution on the victim's setup.

## References
- https://github.com/b2evolution/b2evolution/commit/0096a3ebc85f6aadbda2c4427cd092a538b161d2
- https://github.com/b2evolution/b2evolution/commit/b899d654d931f3bf3cfbbdd71e0d1a0f3a16d04c
