# [H] BIT-libpython-2020-10735

## Summary
Severity: High
Advisory: BIT-libpython-2020-10735
Aliases: BIT-python-2020-10735, BIT-python-min-2020-10735, CVE-2020-10735, PSF-2022-4
Ecosystem: Bitnami
Published: 2025-08-11
Source: https://osv.dev/vulnerability/BIT-libpython-2020-10735
Type: osv

## Affected
- Bitnami: `libpython` — affected >=3.10.0 <3.10.7

## Details
A flaw was found in python. In algorithms with quadratic time complexity using non-binary bases, when using int("text"), a system could take 50ms to parse an int string with 100,000 digits and 5s for 1,000,000 digits (float, decimal, int.from_bytes(), and int() for binary bases 2, 4, 8, 16, and 32 are not affected). The highest threat from this vulnerability is to system availability.

## References
- http://www.openwall.com/lists/oss-security/2022/09/21/1
- http://www.openwall.com/lists/oss-security/2022/09/21/4
- https://access.redhat.com/security/cve/CVE-2020-10735
- https://bugzilla.redhat.com/show_bug.cgi?id=1834423
- https://docs.google.com/document/d/1KjuF_aXlzPUxTK4BMgezGJ2Pn7uevfX7g0_mvgHlL7Y
- https://github.com/python/cpython/issues/95778
- https://lists.debian.org/debian-lts-announce/2023/06/msg00039.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/2VCU6EVQDIXNCEDJUCTFIER2WVNNDTYZ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/32AAQKABEKFCB5DDV5OONRZK6BS23HPW/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/4EWKR2SPX3JORLWCXFY3KN2U5B5CIUQQ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/6XL6E5A3I36TRR73VNBOXNIQP4AMZDFZ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/76YE7AM37MRU76XJV4M27CWDAMUGNRYK/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/HSRPVJZL6DJFWKYRHMNJB7VCEUCBKRF5/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/IFGV7P2PYFBMK32OKHCAC2ZPJQV5AUDF/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/NHC6IUU7CLRQ3QLPWUXLONSG3SXFTR47/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/OKYE2DOI2X7WZXAWTQJZAXYIWM37HDCY/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/OT5U223OE5ZOUHZAZYSYSWVJQIKDE73E/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/OT5WQB7Z3CXOWVBD2AFAHYPA5ONYFFZ4/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/PD7FTLJOIGMUSCDR3JAN6WRFHJEE4PH5/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/SZYJSGLSCQOKXXFVJVJQAXLEOJBIWGEL/
