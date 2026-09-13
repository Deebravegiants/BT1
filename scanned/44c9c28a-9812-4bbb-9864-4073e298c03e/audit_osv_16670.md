# [H] CVE-2019-9022

## Summary
Severity: High
Advisory: CVE-2019-9022
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-02-22
Source: https://osv.dev/vulnerability/CVE-2019-9022
Type: osv

## Details
An issue was discovered in PHP 7.x before 7.1.26, 7.2.x before 7.2.14, and 7.3.x before 7.3.2. dns_get_record misparses a DNS response, which can allow a hostile DNS server to cause PHP to misuse memcpy, leading to read operations going past the buffer allocated for DNS data. This affects php_parserr in ext/standard/dns.c for DNS_CAA and DNS_ANY queries.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-06/msg00041.html
- http://lists.opensuse.org/opensuse-security-announce/2019-06/msg00044.html
- https://www.tenable.com/security/tns-2019-07
- https://access.redhat.com/errata/RHSA-2019:2519
- https://access.redhat.com/errata/RHSA-2019:3299
- https://lists.debian.org/debian-lts-announce/2019/03/msg00043.html
- https://security.netapp.com/advisory/ntap-20190321-0001/
- https://usn.ubuntu.com/3902-1/
- https://usn.ubuntu.com/3922-2/
- https://usn.ubuntu.com/3922-3/
- https://www.debian.org/security/2019/dsa-4398
- https://bugs.php.net/bug.php?id=77369
