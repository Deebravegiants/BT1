# [M] CVE-2022-23034

## Summary
Severity: Medium
Advisory: CVE-2022-23034
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-01-25
Source: https://osv.dev/vulnerability/CVE-2022-23034
Type: osv

## Details
A PV guest could DoS Xen while unmapping a grant To address XSA-380, reference counting was introduced for grant mappings for the case where a PV guest would have the IOMMU enabled. PV guests can request two forms of mappings. When both are in use for any individual mapping, unmapping of such a mapping can be requested in two steps. The reference count for such a mapping would then mistakenly be decremented twice. Underflow of the counters gets detected, resulting in the triggering of a hypervisor bug check.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/OMR6UBGJW6JKND7IILGQ2CU35EQPF3E3/
- http://www.openwall.com/lists/oss-security/2022/01/25/3
- https://security.gentoo.org/glsa/202208-23
- https://www.debian.org/security/2022/dsa-5117
- https://xenbits.xenproject.org/xsa/advisory-394.txt
