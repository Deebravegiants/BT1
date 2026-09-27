# [H] CVE-2021-31783

## Summary
Severity: High
Advisory: CVE-2021-31783
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-04-26
Source: https://osv.dev/vulnerability/CVE-2021-31783
Type: osv

## Details
show_default.php in the LocalFilesEditor extension before 11.4.0.1 for Piwigo allows Local File Inclusion because the file parameter is not validated with a proper regular-expression check.

## References
- https://piwigo.org/ext/index.php?cid=null
- https://github.com/Piwigo/LocalFilesEditor/issues/2
- https://github.com/Piwigo/LocalFilesEditor/commit/dda691d3e45bfd166ac175c70bd8b91cb4917b6b
