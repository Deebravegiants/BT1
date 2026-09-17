# [H] qed: Don't collect too many protection override GRC elements

## Summary
Severity: High
Advisory: CVE-2025-39949
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-04
Source: https://osv.dev/vulnerability/CVE-2025-39949
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.18.0 <5.10.245, >=5.11.0 <5.15.194, >=5.16.0 <6.1.154, >=6.2.0 <6.6.108, >=6.7.0 <6.12.49, >=6.13.0 <6.16.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

qed: Don't collect too many protection override GRC elements

In the protection override dump path, the firmware can return far too
many GRC elements, resulting in attempting to write past the end of the
previously-kmalloc'ed dump buffer.

This will result in a kernel panic with reason:

 BUG: unable to handle kernel paging request at ADDRESS

where "ADDRESS" is just past the end of the protection override dump
buffer. The start address of the buffer is:
 p_hwfn->cdev->dbg_features[DBG_FEATURE_PROTECTION_OVERRIDE].dump_buf
and the size of the buffer is buf_size in the same data structure.

The panic can be arrived at from either the qede Ethernet driver path:

    [exception RIP: qed_grc_dump_addr_range+0x108]
 qed_protection_override_dump at ffffffffc02662ed [qed]
 qed_dbg_protection_override_dump at ffffffffc0267792 [qed]
 qed_dbg_feature at ffffffffc026aa8f [qed]
 qed_dbg_all_data at ffffffffc026b211 [qed]
 qed_fw_fatal_reporter_dump at ffffffffc027298a [qed]
 devlink_health_do_dump at ffffffff82497f61
 devlink_health_report at ffffffff8249cf29
 qed_report_fatal_error at ffffffffc0272baf [qed]
 qede_sp_task at ffffffffc045ed32 [qede]
 process_one_work at ffffffff81d19783

or the qedf storage driver path:

    [exception RIP: qed_grc_dump_addr_range+0x108]
 qed_protection_override_dump at ffffffffc068b2ed [qed]
 qed_dbg_protection_override_dump at ffffffffc068c792 [qed]
 qed_dbg_feature at ffffffffc068fa8f [qed]
 qed_dbg_all_data at ffffffffc0690211 [qed]
 qed_fw_fatal_reporter_dump at ffffffffc069798a [qed]
 devlink_health_do_dump at ffffffff8aa95e51
 devlink_health_report at ffffffff8aa9ae19
 qed_report_fatal_error at ffffffffc0697baf [qed]
 qed_hw_err_notify at ffffffffc06d32d7 [qed]
 qed_spq_post at ffffffffc06b1011 [qed]
 qed_fcoe_destroy_conn at ffffffffc06b2e91 [qed]
 qedf_cleanup_fcport at ffffffffc05e7597 [qedf]
 qedf_rport_event_handler at ffffffffc05e7bf7 [qedf]
 fc_rport_work at ffffffffc02da715 [libfc]
 process_one_work at ffffffff8a319663

Resolve this by clamping the firmware's return value to the maximum
number of legal elements the firmware should return.

## References
- https://git.kernel.org/stable/c/25672c620421fa2105703a94a29a03487245e6d6
- https://git.kernel.org/stable/c/56c0a2a9ddc2f5b5078c5fb0f81ab76bbc3d4c37
- https://git.kernel.org/stable/c/660b2a8f5a306a28c7efc1b4990ecc4912a68f87
- https://git.kernel.org/stable/c/70affe82e38fd3dc76b9c68b5a1989f11e7fa0f3
- https://git.kernel.org/stable/c/8141910869596b7a3a5d9b46107da2191d523f82
- https://git.kernel.org/stable/c/e0e24571a7b2f8c8f06e25d3417253ebbdbc8d5c
- https://git.kernel.org/stable/c/ea53e6a47e148b490b1c652fc65d2de5a086df76
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39949.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39949
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
