# [C] scsi: target: iscsi: Bound iscsi_encode_text_output() appends to rsp_buf

## Summary
Severity: Critical
Advisory: CVE-2026-63887
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-63887
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.1.0 <5.10.259, >=5.11.0 <5.15.210, >=5.16.0 <6.1.176, >=6.2.0 <6.6.143, >=6.7.0 <6.12.93, >=6.13.0 <6.18.35, >=6.19.0 <7.0.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

scsi: target: iscsi: Bound iscsi_encode_text_output() appends to rsp_buf

iscsi_encode_text_output() concatenates "key=value\0" records into
login->rsp_buf, an 8192-byte kzalloc(MAX_KEY_VALUE_PAIRS) buffer
allocated in iscsit_alloc_login_setup_buffer(). The three sprintf() call
sites in this function (lines 1398, 1411, 1424 in v7.1-rc2) never check
the remaining buffer capacity:

	*length += sprintf(output_buf, "%s=%s", er->key, er->value);
	*length += 1;
	output_buf = textbuf + *length;

The 8192-byte ceiling at iscsi_target_check_login_request() bounds the
*input* Login PDU payload, but a single PDU can carry up to 2048 minimal
four-byte "a=b\0" pairs, each unknown key expanding to a 16-byte
"a=NotUnderstood\0" output record via iscsi_add_notunderstood_response().
2048 * 16 = 32 KiB of output into an 8 KiB buffer, producing a ~24 KiB
heap overrun in the kmalloc-8k slab.

The fix introduces a static iscsi_encode_text_record() helper that uses
snprintf() with a per-call bounds check against the remaining buffer,
and threads a u32 textbuf_size parameter through
iscsi_encode_text_output(). Both call sites in
iscsi_target_handle_csg_zero() (PHASE_SECURITY) and
iscsi_target_handle_csg_one() (PHASE_OPERATIONAL) pass
MAX_KEY_VALUE_PAIRS. On overflow the encoder logs the condition, calls
iscsi_release_extra_responses() to drop queued records, and returns -1;
both caller sites now emit ISCSI_STATUS_CLS_INITIATOR_ERR /
ISCSI_LOGIN_STATUS_INIT_ERR via iscsit_tx_login_rsp() before returning,
so the initiator sees an explicit failed-login response rather than a
silent connection drop. (Prior to this patch only the PHASE_OPERATIONAL
caller did that; the PHASE_SECURITY caller is converted to the same
shape.)

## References
- https://git.kernel.org/stable/c/26e4a304b7e6f1338c675d527608d32549c091db
- https://git.kernel.org/stable/c/30bf335e8fe170322080ee001f05ca29c50680b3
- https://git.kernel.org/stable/c/4e9f0c4a645c995bc75c06c7b3644254ffb4c76b
- https://git.kernel.org/stable/c/594a40360012ce5f94c715d5e3b20fa3af7d525a
- https://git.kernel.org/stable/c/b19382dfc6e7dee6d3859ba44b6ca29e97a51627
- https://git.kernel.org/stable/c/bf33e01f88388c43e285492a63e539df6ffed64c
- https://git.kernel.org/stable/c/cb84e974fb172bc71386289f37b78ea679410b39
- https://git.kernel.org/stable/c/efe633e600a0ac68357206fede21b1ac8178f3b8
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63887.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-63887
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
