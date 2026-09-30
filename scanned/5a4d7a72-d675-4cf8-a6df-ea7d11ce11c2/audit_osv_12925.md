# [H] CVE-2018-16388

## Summary
Severity: High
Advisory: CVE-2018-16388
CVSS: 7.2 (CVSS:3.0/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-09-12
Source: https://osv.dev/vulnerability/CVE-2018-16388
Type: osv

## Details
e107_web/js/plupload/upload.php in e107 2.1.8 allows remote attackers to execute arbitrary PHP code by uploading a .php filename with the image/jpeg content type.

## References
- https://github.com/e107inc/e107/commit/e5bb5297f68e56537c004cdbb48a30892e9f6f4c
- https://gist.github.com/ommadawn46/5cb22e7c66cc32a5c7734a8064b4d3f5
