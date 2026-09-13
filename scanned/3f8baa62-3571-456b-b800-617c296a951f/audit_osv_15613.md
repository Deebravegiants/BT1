# [H] CVE-2019-17596

## Summary
Severity: High
Advisory: CVE-2019-17596
Aliases: GO-2022-0213
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-10-24
Source: https://osv.dev/vulnerability/CVE-2019-17596
Type: osv

## Details
Go before 1.12.11 and 1.3.x before 1.13.2 can panic upon an attempt to process network traffic containing an invalid DSA public key. There are several attack scenarios, such as traffic from a client to a server that verifies client certificates.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/5VS3HPSE25ZSGS4RSOTADC67YNOHIGVV/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/WVOWGM7IQGRO7DS2MCUMYZRQ4TYOZNAS/
- http://lists.opensuse.org/opensuse-security-announce/2019-11/msg00043.html
- http://lists.opensuse.org/opensuse-security-announce/2019-11/msg00044.html
- https://access.redhat.com/errata/RHSA-2020:0101
- https://access.redhat.com/errata/RHSA-2020:0329
- https://groups.google.com/d/msg/golang-announce/lVEm7llp0w0/VbafyRkgCgAJ
- https://lists.debian.org/debian-lts-announce/2021/03/msg00014.html
- https://lists.debian.org/debian-lts-announce/2021/03/msg00015.html
- https://security.netapp.com/advisory/ntap-20191122-0005/
- https://www.arista.com/en/support/advisories-notices/security-advisories/10134-security-advisory-46
- https://www.debian.org/security/2019/dsa-4551
- https://github.com/golang/go/issues/34960
