# [C] CVE-2017-12065

## Summary
Severity: Critical
Advisory: CVE-2017-12065
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-08-01
Source: https://osv.dev/vulnerability/CVE-2017-12065
Type: osv

## Details
spikekill.php in Cacti before 1.1.16 might allow remote attackers to execute arbitrary code via the avgnan, outlier-start, or outlier-end parameter.

## References
- http://www.securityfocus.com/bid/100080
- https://cacti.net/release_notes.php?version=1.1.16
- https://security.gentoo.org/glsa/201711-10
- https://github.com/Cacti/cacti/commit/bd0e586f6f46d814930226f1516a194e7e72293e
- https://github.com/Cacti/cacti/issues/877
