# [M] CVE-2019-25031

## Summary
Severity: Medium
Advisory: CVE-2019-25031
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2021-04-27
Source: https://osv.dev/vulnerability/CVE-2019-25031
Type: osv

## Details
Unbound before 1.9.5 allows configuration injection in create_unbound_ad_servers.sh upon a successful man-in-the-middle attack against a cleartext HTTP session. NOTE: The vendor does not consider this a vulnerability of the Unbound software. create_unbound_ad_servers.sh is a contributed script from the community that facilitates automatic configuration creation. It is not part of the Unbound installation

## References
- https://lists.debian.org/debian-lts-announce/2021/05/msg00007.html
- https://ostif.org/our-audit-of-unbound-dns-by-x41-d-sec-full-results/
- https://security.netapp.com/advisory/ntap-20210507-0007/
