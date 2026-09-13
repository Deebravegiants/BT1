# [M] CVE-2017-11368

## Summary
Severity: Medium
Advisory: CVE-2017-11368
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-08-09
Source: https://osv.dev/vulnerability/CVE-2017-11368
Type: osv

## Details
In MIT Kerberos 5 (aka krb5) 1.7 and later, an authenticated attacker can cause a KDC assertion failure by sending invalid S4U2Self or S4U2Proxy requests.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/4HNWXM6OQU7G23MG7XWIOBRGP43ECLDT/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/UBUTXMNZWMVJLQ4NDX5OQFPUVCJRLV3W/
- http://www.securityfocus.com/bid/100291
- https://access.redhat.com/errata/RHSA-2018:0666
- https://github.com/krb5/krb5/commit/ffb35baac6981f9e8914f8f3bffd37f284b85970
