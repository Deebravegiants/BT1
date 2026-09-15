# [H] CVE-2016-7037

## Summary
Severity: High
Advisory: CVE-2016-7037
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2017-01-23
Source: https://osv.dev/vulnerability/CVE-2016-7037
Type: osv

## Details
The verify function in Encryption/Symmetric.php in Malcolm Fell jwt before 1.0.3 does not use a timing-safe function for hash comparison, which allows attackers to spoof signatures via a timing attack.

## References
- http://www.securityfocus.com/bid/95847
- https://github.com/emarref/jwt/pull/20
- https://github.com/emarref/jwt/releases/tag/1.0.3
