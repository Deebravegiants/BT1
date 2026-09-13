# [H] CVE-2018-19205

## Summary
Severity: High
Advisory: CVE-2018-19205
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-11-12
Source: https://osv.dev/vulnerability/CVE-2018-19205
Type: osv

## Details
Roundcube before 1.3.7 mishandles GnuPG MDC integrity-protection warnings, which makes it easier for attackers to obtain sensitive information, a related issue to CVE-2017-17688. This is associated with plugins/enigma/lib/enigma_driver_gnupg.php.

## References
- https://github.com/roundcube/roundcubemail/releases/tag/1.3.7
- https://roundcube.net/news/2018/07/27/update-1.3.7-released
