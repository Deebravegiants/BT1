# [C] CVE-2018-17831

## Summary
Severity: Critical
Advisory: CVE-2018-17831
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-10-01
Source: https://osv.dev/vulnerability/CVE-2018-17831
Type: osv

## Details
In REDAXO before 5.6.3, a critical SQL injection vulnerability has been discovered in the rex_list class because of the prepareQuery function in core/lib/list.php, via the index.php?page=users/users sort parameter. Endangered was the backend and the frontend only if rex_list were used.

## References
- https://github.com/redaxo/redaxo/releases/tag/5.6.3
- https://redaxo.org/cms/news/sicherheitsluecke-und-neue-yform-version/
- https://github.com/redaxo/redaxo/issues/2043
