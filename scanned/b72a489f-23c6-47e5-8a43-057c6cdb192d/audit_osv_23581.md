# [H] scsi: qla2xxx: Fix crash during module load unload test

## Summary
Severity: High
Advisory: CVE-2022-49160
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:A/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49160
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.9.0 <5.15.54, >=5.16.0 <5.16.19, >=5.17.0 <5.17.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

scsi: qla2xxx: Fix crash during module load unload test

During purex packet handling the driver was incorrectly freeing a
pre-allocated structure. Fix this by skipping that entry.

System crashed with the following stack during a module unload test.

Call Trace:
	sbitmap_init_node+0x7f/0x1e0
	sbitmap_queue_init_node+0x24/0x150
	blk_mq_init_bitmaps+0x3d/0xa0
	blk_mq_init_tags+0x68/0x90
	blk_mq_alloc_map_and_rqs+0x44/0x120
	blk_mq_alloc_set_map_and_rqs+0x63/0x150
	blk_mq_alloc_tag_set+0x11b/0x230
	scsi_add_host_with_dma.cold+0x3f/0x245
	qla2x00_probe_one+0xd5a/0x1b80 [qla2xxx]

Call Trace with slub_debug and debug kernel:
	kasan_report_invalid_free+0x50/0x80
	__kasan_slab_free+0x137/0x150
	slab_free_freelist_hook+0xc6/0x190
	kfree+0xe8/0x2e0
	qla2x00_free_device+0x3bb/0x5d0 [qla2xxx]
	qla2x00_remove_one+0x668/0xcf0 [qla2xxx]

## References
- https://git.kernel.org/stable/c/0972252450f90db56dd5415a20e2aec21a08d036
- https://git.kernel.org/stable/c/213e57b42537f1a2e5395caa9d7189854133ed12
- https://git.kernel.org/stable/c/67f744f73eba870ab96411d0310e831a4adc3713
- https://git.kernel.org/stable/c/9b7eb92dac240ab3bc83e188d83a3df834b41eb2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49160.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49160
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
