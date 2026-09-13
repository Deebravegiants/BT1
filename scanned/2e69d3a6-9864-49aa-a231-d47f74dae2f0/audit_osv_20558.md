# [M] CVE-2021-3509

## Summary
Severity: Medium
Advisory: CVE-2021-3509
CVSS: 6.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N)
Published: 2021-05-27
Source: https://osv.dev/vulnerability/CVE-2021-3509
Type: osv

## Details
A flaw was found in Red Hat Ceph Storage 4, in the Dashboard component. In response to CVE-2020-27839, the JWT token was moved from localStorage to an httpOnly cookie. However, token cookies are used in the body of the HTTP response for the documentation, which again makes it available to XSS.The greatest threat to the system is for confidentiality, integrity, and availability.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1950116
- https://github.com/ceph/ceph/commit/7a1ca8d372da3b6a4fc3d221a0e5f72d1d61c27b
- https://github.com/ceph/ceph/commit/adda853e64bdba1288d46bc7d462d23d8f2f10ca
- https://github.com/ceph/ceph/commit/af3fffab3b0f13057134d96e5d481e400d8bfd27
- https://github.com/ceph/ceph/blob/f1557e8f62d31883d3d34ae241a1a26af11d923f/src/pybind/mgr/dashboard/controllers/docs.py#L394-L409
