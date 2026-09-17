# [H] BIT-libpython-2020-26116

## Summary
Severity: High
Advisory: BIT-libpython-2020-26116
Aliases: BIT-python-2020-26116, BIT-python-min-2020-26116, CVE-2020-26116, PSF-2020-5
Ecosystem: Bitnami
Published: 2025-08-11
Source: https://osv.dev/vulnerability/BIT-libpython-2020-26116
Type: osv

## Affected
- Bitnami: `libpython` — affected >=3.8.0 <3.8.5

## Details
http.client in Python 3.x before 3.5.10, 3.6.x before 3.6.12, 3.7.x before 3.7.9, and 3.8.x before 3.8.5 allows CRLF injection if the attacker controls the HTTP request method, as demonstrated by inserting CR and LF control characters in the first argument of HTTPConnection.request.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-11/msg00027.html
- https://bugs.python.org/issue39603
- https://lists.debian.org/debian-lts-announce/2020/11/msg00032.html
- https://lists.debian.org/debian-lts-announce/2023/05/msg00024.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/BW4GCLQISJCOEGQNIMVUZDQMIY6RR6CC/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/HDQ2THWU4GPV4Y5H5WW5PFMSWXL2CRFD/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/JWMAVY4T4257AZHTF2RZJKNJNSJFY24O/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/OXI72HIHMXCQFWTULUXDG7VDA2BCYL4Y/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/QOX7DGMMWWL6POCRYGAUCISOLR2IG3XV/
- https://nvd.nist.gov/vuln/detail/CVE-2020-26116
- https://python-security.readthedocs.io/vuln/http-header-injection-method.html
- https://security.gentoo.org/glsa/202101-18
- https://security.netapp.com/advisory/ntap-20201023-0001/
- https://usn.ubuntu.com/4581-1/
- https://www.oracle.com/security-alerts/cpuoct2021.html
