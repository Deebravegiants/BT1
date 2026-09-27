# [M] CVE-2020-35496

## Summary
Severity: Medium
Advisory: CVE-2020-35496
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-01-04
Source: https://osv.dev/vulnerability/CVE-2020-35496
Type: osv

## Details
There's a flaw in bfd_pef_scan_start_address() of bfd/pef.c in binutils which could allow an attacker who is able to submit a crafted file to be processed by objdump to cause a NULL pointer dereference. The greatest threat of this flaw is to application availability. This flaw affects binutils versions prior to 2.34.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/4KOK3QWSVOUJWJ54HVGIFWNLWQ5ZY4S6/
- https://security.gentoo.org/glsa/202107-24
- https://security.netapp.com/advisory/ntap-20210212-0007/
- https://bugzilla.redhat.com/show_bug.cgi?id=1911444
