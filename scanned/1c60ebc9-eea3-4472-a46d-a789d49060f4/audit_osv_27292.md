# [H] net: nexthop: Increase weight to u16

## Summary
Severity: High
Advisory: CVE-2024-14040
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-26
Source: https://osv.dev/vulnerability/CVE-2024-14040
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: nexthop: Increase weight to u16

In CLOS networks, as link failures occur at various points in the network,
ECMP weights of the involved nodes are adjusted to compensate. With high
fan-out of the involved nodes, and overall high number of nodes,
a (non-)ECMP weight ratio that we would like to configure does not fit into
8 bits. Instead of, say, 255:254, we might like to configure something like
1000:999. For these deployments, the 8-bit weight may not be enough.

To that end, in this patch increase the next hop weight from u8 to u16.

Increasing the width of an integral type can be tricky, because while the
code still compiles, the types may not check out anymore, and numerical
errors come up. To prevent this, the conversion was done in two steps.
First the type was changed from u8 to a single-member structure, which
invalidated all uses of the field. This allowed going through them one by
one and audit for type correctness. Then the structure was replaced with a
vanilla u16 again. This should ensure that no place was missed.

The UAPI for configuring nexthop group members is that an attribute
NHA_GROUP carries an array of struct nexthop_grp entries:

	struct nexthop_grp {
		__u32	id;	  /* nexthop id - must exist */
		__u8	weight;   /* weight of this nexthop */
		__u8	resvd1;
		__u16	resvd2;
	};

The field resvd1 is currently validated and required to be zero. We can
lift this requirement and carry high-order bits of the weight in the
reserved field:

	struct nexthop_grp {
		__u32	id;	  /* nexthop id - must exist */
		__u8	weight;   /* weight of this nexthop */
		__u8	weight_high;
		__u16	resvd2;
	};

Keeping the fields split this way was chosen in case an existing userspace
makes assumptions about the width of the weight field, and to sidestep any
endianness issues.

The weight field is currently encoded as the weight value minus one,
because weight of 0 is invalid. This same trick is impossible for the new
weight_high field, because zero must mean actual zero. With this in place:

- Old userspace is guaranteed to carry weight_high of 0, therefore
  configuring 8-bit weights as appropriate. When dumping nexthops with
  16-bit weight, it would only show the lower 8 bits. But configuring such
  nexthops implies existence of userspace aware of the extension in the
  first place.

- New userspace talking to an old kernel will work as long as it only
  attempts to configure 8-bit weights, where the high-order bits are zero.
  Old kernel will bounce attempts at configuring >8-bit weights.

Renaming reserved fields as they are allocated for some purpose is commonly
done in Linux. Whoever touches a reserved field is doing so at their own
risk. nexthop_grp::resvd1 in particular is currently used by at least
strace, however they carry an own copy of UAPI headers, and the conversion
should be trivial. A helper is provided for decoding the weight out of the
two fields. Forcing a conversion seems preferable to bending backwards and
introducing anonymous unions or whatever.

## References
- https://git.kernel.org/stable/c/b72a6a7ab9573e06d5c2fcb92eaa28614a735bfd
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/14xxx/CVE-2024-14040.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-14040
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
