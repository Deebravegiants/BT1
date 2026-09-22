# [H] CVE-2016-4425

## Summary
Severity: High
Advisory: CVE-2016-4425
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-05-17
Source: https://osv.dev/vulnerability/CVE-2016-4425
Type: osv

## Details
Jansson 2.7 and earlier allows context-dependent attackers to cause a denial of service (deep recursion, stack consumption, and crash) via crafted JSON data.

## References
- http://www.openwall.com/lists/oss-security/2016/05/01/5
- http://www.openwall.com/lists/oss-security/2016/05/02/1
- http://www.openwall.com/lists/oss-security/2016/05/03/3
- https://github.com/akheron/jansson/pull/284/commits/64ce0ad3731ebd77e02897b07920eadd0e2cc318
- http://www.debian.org/security/2015/dsa-3577
- https://github.com/akheron/jansson/issues/282
- https://github.com/akheron/jansson/pull/284
