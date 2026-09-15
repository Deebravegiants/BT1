# [H] udf: fix partition descriptor append bookkeeping

## Summary
Severity: High
Advisory: CVE-2026-45991
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-27
Source: https://osv.dev/vulnerability/CVE-2026-45991
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.19.0 <5.10.259, >=5.11.0 <5.15.210, >=5.16.0 <6.1.176, >=6.2.0 <6.6.140, >=6.7.0 <6.12.88, >=6.13.0 <7.0.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

udf: fix partition descriptor append bookkeeping

Mounting a crafted UDF image with repeated partition descriptors can
trigger a heap out-of-bounds write in part_descs_loc[].

handle_partition_descriptor() deduplicates entries by partition number,
but appended slots never record partnum. As a result duplicate
Partition Descriptors are appended repeatedly and num_part_descs keeps
growing.

Once the table is full, the growth path still sizes the allocation from
partnum even though inserts are indexed by num_part_descs. If partnum is
already aligned to PART_DESC_ALLOC_STEP, ALIGN(partnum, step) can keep
the old capacity and the next append writes past the end of the table.

Store partnum in the appended slot and size growth from the next append
count so deduplication and capacity tracking follow the same model.

## References
- https://git.kernel.org/stable/c/058b451b1039f056d1362c4fec2229e522366ab0
- https://git.kernel.org/stable/c/08841b06fa64d8edbd1a21ca6e613420c90cc4b8
- https://git.kernel.org/stable/c/08fa5d818e5bf53c7ca234d88ba334f32004e9b6
- https://git.kernel.org/stable/c/68013a9bd4c01acd42073715f00e1a1992f089ee
- https://git.kernel.org/stable/c/ad3c0c4400686f6f37b382aaa48fac2b9aefccbe
- https://git.kernel.org/stable/c/b5597bb83fc37b5b5da74a4453fa920b932cf39a
- https://git.kernel.org/stable/c/e8474cfbac9ada2cdaa4eaedec22aadfa0f58559
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45991.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-45991
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
