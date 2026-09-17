# [H] udf: validate VAT header length against the VAT inode size

## Summary
Severity: High
Advisory: CVE-2026-64323
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-07-25
Source: https://osv.dev/vulnerability/CVE-2026-64323
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.26 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.96, >=6.13.0 <6.18.39, >=6.19.0 <7.1.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

udf: validate VAT header length against the VAT inode size

udf_load_vat() takes the virtual partition's start offset straight from
the on-disk VAT 2.0 header without checking it against the VAT inode
size:

	map->s_type_specific.s_virtual.s_start_offset =
		le16_to_cpu(vat20->lengthHeader);
	map->s_type_specific.s_virtual.s_num_entries =
		(sbi->s_vat_inode->i_size -
			map->s_type_specific.s_virtual.s_start_offset) >> 2;

lengthHeader is a fully attacker-controlled 16-bit value.  If it exceeds
the VAT inode size, the s_num_entries subtraction underflows to a huge
count, which defeats the "block > s_num_entries" bound in
udf_get_pblock_virt15(); and on the ICB-inline path that function reads

	((__le32 *)(iinfo->i_data + s_start_offset))[block]

so a large s_start_offset indexes past the inode's in-ICB data.  Mounting
a crafted UDF image with a virtual (VAT) partition then triggers an
out-of-bounds read.

Reject a VAT whose header length does not leave room for at least one
entry within the VAT inode.

## References
- https://git.kernel.org/stable/c/0ad2d09a8d66fa8dc6f9b70d660b5fb4478ea934
- https://git.kernel.org/stable/c/2900e02a0dd4fc30ac9840e7ce4ca0b041ab0d63
- https://git.kernel.org/stable/c/55287a3555ff0515b3aff181d2c08c0462a41709
- https://git.kernel.org/stable/c/74580fdf022909e184223cacc364feb826982d96
- https://git.kernel.org/stable/c/883962731420ec271ed8c1cd76524f4b17faa982
- https://git.kernel.org/stable/c/bb0d384c1f42a5b7ace0bd88fee80b9bb1d49acb
- https://git.kernel.org/stable/c/d8202786b3d75125c84ebc4de6d946f92fde0ee8
- https://git.kernel.org/stable/c/e610fb113cdfa8bf4247c9bf4f2337b81ad4ddad
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64323.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64323
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
