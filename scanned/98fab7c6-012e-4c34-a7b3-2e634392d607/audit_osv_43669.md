# [H] scsi: libiscsi: Fix stale-data leak into the SCSI sense buffer

## Summary
Severity: High
Advisory: CVE-2026-74557
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74557
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.18 <5.10.265, >=5.11.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.151, >=6.7.0 <6.12.103, >=6.13.0 <6.18.44, >=6.19.0 <7.1.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

scsi: libiscsi: Fix stale-data leak into the SCSI sense buffer

iscsi_scsi_cmd_rsp() copies the sense data of a SCSI Response from the
target-supplied data segment.  The segment carries a 2-byte sense length
followed by the sense bytes, so it must hold 2 + senselen bytes, but the
bounds check only requires datalen >= senselen:

	senselen = get_unaligned_be16(data);
	if (datalen < senselen)
		goto invalid_datalen;
	memcpy(sc->sense_buffer, data + 2,
	       min_t(uint16_t, senselen, SCSI_SENSE_BUFFERSIZE));

A target that returns a SCSI Response whose datalen equals senselen
(with senselen <= SCSI_SENSE_BUFFERSIZE) makes the memcpy() from data +
2 read up to two bytes past the received data.  Those bytes are stale
conn->data contents and end up in the command's sense buffer, which is
returned to userspace.

Account for the 2-byte sense length prefix in the check.

## References
- https://git.kernel.org/stable/c/1f07a897d43c63e6c9458bf77450defef39b5833
- https://git.kernel.org/stable/c/3ef209ca0b4b68c75e9a814d90cc916026b5a6ac
- https://git.kernel.org/stable/c/60499924faf4ef97e84228c20515218ef121facf
- https://git.kernel.org/stable/c/7567f06abdefb1caf2d836107c4d08c5185c650e
- https://git.kernel.org/stable/c/812f1ae95b22419422972748f173b0916ee4d621
- https://git.kernel.org/stable/c/98b87885de4b7f605533a2860685f5689fce8e82
- https://git.kernel.org/stable/c/baa04572673125e4d5bc309b4077d1cb46cc78d1
- https://git.kernel.org/stable/c/fef6167e8149896cd81bea333fd51b1c91239149
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74557.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74557
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
