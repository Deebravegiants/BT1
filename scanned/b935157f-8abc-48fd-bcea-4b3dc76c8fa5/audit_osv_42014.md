# [H] udf: validate sparing table length as an entry count, not a byte count

## Summary
Severity: High
Advisory: CVE-2026-64322
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-25
Source: https://osv.dev/vulnerability/CVE-2026-64322
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.5.0 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.96, >=6.13.0 <6.18.39, >=6.19.0 <7.1.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

udf: validate sparing table length as an entry count, not a byte count

udf_load_sparable_map() accepts a sparing table when

	sizeof(*st) + le16_to_cpu(st->reallocationTableLen) > sb->s_blocksize

is false, i.e. it treats reallocationTableLen as a number of BYTES that
must fit in the block.  But the table is walked as an array of 8-byte
sparingEntry elements:

	for (i = 0; i < le16_to_cpu(st->reallocationTableLen); i++) {
		struct sparingEntry *entry = &st->mapEntry[i];
		... entry->origLocation ...
	}

in udf_get_pblock_spar15() and udf_relocate_blocks().  A
reallocationTableLen of N therefore passes the check whenever
sizeof(*st) + N <= blocksize, yet the consumers index
sizeof(*st) + N * sizeof(struct sparingEntry) bytes -- up to ~8x the
block.  On a crafted UDF image this is an out-of-bounds read in
udf_get_pblock_spar15(); udf_relocate_blocks() additionally feeds the
same length to udf_update_tag(), whose crc_itu_t() reads far past the
block, and its memmove() through st->mapEntry[] is an out-of-bounds
write.

Validate reallocationTableLen as the entry count it is, with
struct_size().

## References
- https://git.kernel.org/stable/c/04f4599a9efb90992d072a814960edf0cd62805d
- https://git.kernel.org/stable/c/0a9b79a951cfd70a9d31ca01ae2d08a20bb730e9
- https://git.kernel.org/stable/c/2a219acb2ce674d99bbd1b7b35ed8c384dac7200
- https://git.kernel.org/stable/c/2d726135099313958f8975532a2e15322ff150ce
- https://git.kernel.org/stable/c/3ec997bd5508e9b25210b5bbec89031629cdb093
- https://git.kernel.org/stable/c/7285276aa50d2839afb5957ffd491ad282dc8f72
- https://git.kernel.org/stable/c/7f7774b9da0ef17b87bfa238cf966ad0b3376150
- https://git.kernel.org/stable/c/eeb0f3e193f8e523d03e4c9e084f6b4875f50e8e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64322.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64322
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
