# [M] CVE-2016-10514

## Summary
Severity: Medium
Advisory: CVE-2016-10514
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N)
Published: 2017-10-10
Source: https://osv.dev/vulnerability/CVE-2016-10514
Type: osv

## Details
url_check_format in include/functions.inc.php in Piwigo before 2.8.3 allows remote attackers to bypass intended access restrictions via a URL that contains a " character, or a URL beginning with a substring other than the http:// or https:// substring.

## References
- http://piwigo.org/releases/2.8.3
- https://github.com/Piwigo/Piwigo/commit/b3157cbfd859c914911b114d4edbba4654758b57
- https://github.com/Piwigo/Piwigo/issues/547
