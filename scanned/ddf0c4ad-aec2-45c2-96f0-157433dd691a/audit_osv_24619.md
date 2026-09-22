# [H] CVE-2023-24038

## Summary
Severity: High
Advisory: CVE-2023-24038
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-01-21
Source: https://osv.dev/vulnerability/CVE-2023-24038
Type: osv

## Details
The HTML-StripScripts module through 1.06 for Perl allows _hss_attval_style ReDoS because of catastrophic backtracking for HTML content with certain style attributes.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/4MYD5PFRUUB4VVY52I5KA3RQ7SQOD7YM/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ASDRHN2MLGL2HGBUNDZG4YLUWW6NSUKD/
- https://lists.debian.org/debian-lts-announce/2023/01/msg00036.html
- https://www.debian.org/security/2023/dsa-5339
- https://github.com/clintongormley/perl-html-stripscripts/issues/3
