# [H] CVE-2017-17793

## Summary
Severity: High
Advisory: CVE-2017-17793
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2017-12-20
Source: https://osv.dev/vulnerability/CVE-2017-17793
Type: osv

## Details
Information Disclosure vulnerability in creer_fichier_zip in admin/maintenance.php in BlogoText through 3.7.6 allows remote attackers to defeat a filename-randomization protection mechanism, and read backup archives on Windows servers, by providing the archiv~1.zip name (aka an 8.3 filename).

## References
- https://github.com/BlogoText/blogotext/issues/345
- https://github.com/BlogoText/blogotext/commit/101dc1d37010a1d877d6961ed2f32d089c708e91
