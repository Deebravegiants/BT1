# [H] CVE-2017-14226

## Summary
Severity: High
Advisory: CVE-2017-14226
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-09-09
Source: https://osv.dev/vulnerability/CVE-2017-14226
Type: osv

## Details
WP1StylesListener.cpp, WP5StylesListener.cpp, and WP42StylesListener.cpp in libwpd 0.10.1 mishandle iterators, which allows remote attackers to cause a denial of service (heap-based buffer over-read in the WPXTableList class in WPXTable.cpp). This vulnerability can be triggered in LibreOffice before 5.3.7. It may lead to suffering a remote attack against a LibreOffice application.

## References
- https://cgit.freedesktop.org/libreoffice/core/commit/?id=dd89afa6ee8166b69e7a1e86f22616ca8fc122c9
- https://bugs.documentfoundation.org/show_bug.cgi?id=112269
- https://bugzilla.redhat.com/show_bug.cgi?id=1489337
- https://sourceforge.net/p/libwpd/tickets/14/
- https://sourceforge.net/p/libwpd/code/ci/0329a9c57f9b3b0efa0f09a5235dfd90236803a5/
- https://sourceforge.net/p/libwpd/code/ci/f40827b3eae260ce657c67d9fecc855b09dea3c3/
