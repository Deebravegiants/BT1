# [M] CVE-2016-5430

## Summary
Severity: Medium
Advisory: CVE-2016-5430
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2016-09-03
Source: https://osv.dev/vulnerability/CVE-2016-5430
Type: osv

## Details
The RSA 1.5 algorithm implementation in the JOSE_JWE class in JWE.php in jose-php before 2.2.1 lacks the Random Filling protection mechanism, which makes it easier for remote attackers to obtain cleartext data via a Million Message Attack (MMA).

## References
- http://www.securityfocus.com/bid/92741
- https://github.com/nov/jose-php/commit/f03b986b4439e20b0fd635109b48afe96cf0099b#diff-37b0d289d6375ba4a7740401950ccdd6R199
