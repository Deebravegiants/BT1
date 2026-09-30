# [H] CVE-2017-16248

## Summary
Severity: High
Advisory: CVE-2017-16248
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2017-11-01
Source: https://osv.dev/vulnerability/CVE-2017-16248
Type: osv

## Details
The Catalyst-Plugin-Static-Simple module before 0.34 for Perl allows remote attackers to read arbitrary files if there is a '.' character anywhere in the pathname, which differs from the intended policy of allowing access only when the filename itself has a '.' character.

## References
- https://bugs.debian.org/880458
- https://metacpan.org/changes/distribution/Catalyst-Plugin-Static-Simple
- https://rt.cpan.org/Public/Bug/Display.html?id=120558
