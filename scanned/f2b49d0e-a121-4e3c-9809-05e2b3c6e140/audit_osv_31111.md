# [H] HID: core: Fix assumption that Resolution Multipliers must be in Logical Collections

## Summary
Severity: High
Advisory: CVE-2024-57986
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:H)
Published: 2025-02-27
Source: https://osv.dev/vulnerability/CVE-2024-57986
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.0.0 <5.4.291, >=5.5.0 <5.10.235, >=5.11.0 <5.15.179, >=5.16.0 <6.1.129, >=6.2.0 <6.6.76, >=6.7.0 <6.12.13, >=6.13.0 <6.13.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

HID: core: Fix assumption that Resolution Multipliers must be in Logical Collections

A report in 2019 by the syzbot fuzzer was found to be connected to two
errors in the HID core associated with Resolution Multipliers.  One of
the errors was fixed by commit ea427a222d8b ("HID: core: Fix deadloop
in hid_apply_multiplier."), but the other has not been fixed.

This error arises because hid_apply_multipler() assumes that every
Resolution Multiplier control is contained in a Logical Collection,
i.e., there's no way the routine can ever set multiplier_collection to
NULL.  This is in spite of the fact that the function starts with a
big comment saying:

	 * "The Resolution Multiplier control must be contained in the same
	 * Logical Collection as the control(s) to which it is to be applied.
	   ...
	 *  If no Logical Collection is
	 * defined, the Resolution Multiplier is associated with all
	 * controls in the report."
	 * HID Usage Table, v1.12, Section 4.3.1, p30
	 *
	 * Thus, search from the current collection upwards until we find a
	 * logical collection...

The comment and the code overlook the possibility that none of the
collections found may be a Logical Collection.

The fix is to set the multiplier_collection pointer to NULL if the
collection found isn't a Logical Collection.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://git.kernel.org/stable/c/05dd7d10675b540b8b7b31035c0a8abb6e6f3b88
- https://git.kernel.org/stable/c/3a002e4029230d9a6be89f869b2328b258612f5c
- https://git.kernel.org/stable/c/64f2657b579343cf923aa933f08074e6258eb07b
- https://git.kernel.org/stable/c/a32ea3f982b389ea43a41ce77b6fb70d74006d9b
- https://git.kernel.org/stable/c/a5498f1f864ea26f4c613c77f54409c776a95a90
- https://git.kernel.org/stable/c/bebf542e8d7c44a18a95f306b1b5dc160c823506
- https://git.kernel.org/stable/c/ebaeca33d32c8bdb705a8c88267737a456f354b1
- https://git.kernel.org/stable/c/ed3d3883476423f337aac0f22c521819b3f1e970
- https://lists.debian.org/debian-lts-announce/2025/03/msg00028.html
- https://lists.debian.org/debian-lts-announce/2025/05/msg00030.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/57xxx/CVE-2024-57986.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-57986
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
