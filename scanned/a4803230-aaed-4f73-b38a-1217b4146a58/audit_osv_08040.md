# [H] CVE-2016-10084

## Summary
Severity: High
Advisory: CVE-2016-10084
CVSS: 7.2 (CVSS:3.0/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-12-30
Source: https://osv.dev/vulnerability/CVE-2016-10084
Type: osv

## Details
admin/batch_manager.php in Piwigo through 2.8.3 allows remote authenticated administrators to conduct File Inclusion attacks via the $page['tab'] variable (aka the mode parameter).

## References
- http://www.securityfocus.com/bid/95164
- https://github.com/Piwigo/Piwigo/commit/9dd92959f6975099e0c62163a846a4648a6a920f
- https://github.com/Piwigo/Piwigo/issues/572#issuecomment-268252202
