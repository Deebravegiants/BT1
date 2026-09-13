# [H] CVE-2016-3185

## Summary
Severity: High
Advisory: CVE-2016-3185
CVSS: 7.1 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2016-05-16
Source: https://osv.dev/vulnerability/CVE-2016-3185
Type: osv

## Details
The make_http_soap_request function in ext/soap/php_http.c in PHP before 5.4.44, 5.5.x before 5.5.28, 5.6.x before 5.6.12, and 7.x before 7.0.4 allows remote attackers to obtain sensitive information from process memory or cause a denial of service (type confusion and application crash) via crafted serialized _cookies data, related to the SoapClient::__call method in ext/soap/soap.c.

## References
- http://lists.opensuse.org/opensuse-security-announce/2016-04/msg00052.html
- http://lists.opensuse.org/opensuse-security-announce/2016-04/msg00056.html
- http://lists.opensuse.org/opensuse-security-announce/2016-04/msg00057.html
- http://lists.opensuse.org/opensuse-security-announce/2016-04/msg00058.html
- http://php.net/ChangeLog-5.php
- http://php.net/ChangeLog-7.php
- http://www.securityfocus.com/bid/84307
- https://bugs.php.net/bug.php?id=70081
- https://bugs.php.net/bug.php?id=71610
- https://git.php.net/?p=php-src.git%3Ba=commit%3Bh=eaf4e77190d402ea014207e9a7d5da1a4f3727ba
- http://www.ubuntu.com/usn/USN-2952-1
- http://www.ubuntu.com/usn/USN-2952-2
