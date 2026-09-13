# [M] CVE-2020-35493

## Summary
Severity: Medium
Advisory: CVE-2020-35493
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-01-04
Source: https://osv.dev/vulnerability/CVE-2020-35493
Type: osv

## Details
A flaw exists in binutils in bfd/pef.c. An attacker who is able to submit a crafted PEF file to be parsed by objdump could cause a heap buffer overflow -> out-of-bounds read that could lead to an impact to application availability. This flaw affects binutils versions prior to 2.34.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/4KOK3QWSVOUJWJ54HVGIFWNLWQ5ZY4S6/
- https://security.gentoo.org/glsa/202107-24
- https://security.netapp.com/advisory/ntap-20210212-0007/
- https://bugzilla.redhat.com/show_bug.cgi?id=1911437
