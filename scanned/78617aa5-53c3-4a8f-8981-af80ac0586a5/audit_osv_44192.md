# [H] Input: synaptics-rmi4 - bound the F54 report size to the allocated buffer

## Summary
Severity: High
Advisory: CVE-2026-80569
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-26
Source: https://osv.dev/vulnerability/CVE-2026-80569
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.10.0 <5.10.266, >=5.11.0 <5.15.217, >=5.16.0 <6.1.184, >=6.2.0 <6.6.153, >=6.7.0 <6.12.105, >=6.13.0 <6.18.46, >=6.19.0 <7.1.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

Input: synaptics-rmi4 - bound the F54 report size to the allocated buffer

rmi_f54_work() reads a diagnostics report from the device into
f54->report_data, sizing the transfer with rmi_f54_get_report_size():

	report_size = rmi_f54_get_report_size(f54);
	...
	for (i = 0; i < report_size; i += F54_REPORT_DATA_SIZE) {
		int size = min(F54_REPORT_DATA_SIZE, report_size - i);
		...
		rmi_read_block(.., f54->report_data + i, size);
	}

report_data is allocated once at probe from F54's own electrode counts
(array3_size(f54->num_tx_electrodes, f54->num_rx_electrodes, sizeof(u16))),
but rmi_f54_get_report_size() computes the size from
drv_data->num_*_electrodes when those are set, i.e. from the F55
function's electrode counts. Both counts come straight from device
queries (F54 and F55 each report up to 255 electrodes) and nothing
constrains the F55 counts to the F54 ones.

A malicious or malfunctioning RMI4 device that reports larger F55
electrode counts than its F54 counts makes report_size exceed the
allocation, so the read loop writes past report_data (and the V4L2
dequeue memcpy() then reads past it). On conforming hardware the F55
configured electrodes are a subset of the F54 physical electrodes, so
report_size never exceeds the buffer and well-behaved devices are
unaffected.

Record the allocation size and reject a report that does not fit,
mirroring the existing zero-size check.

## References
- https://git.kernel.org/stable/c/12be3c6ca9589afd6ade41a59c761866e526634d
- https://git.kernel.org/stable/c/42eaf0e6f79c487f419737314cf0760f7331d368
- https://git.kernel.org/stable/c/49c5adc2b7d6e43c5cf033e1c86fdb9c16ababb1
- https://git.kernel.org/stable/c/6b06aab79ff166d5781ce792d91acc2e58b1770b
- https://git.kernel.org/stable/c/6b3bdd44d4cd7d5e35de1d0f06d4930f3cecd403
- https://git.kernel.org/stable/c/b2f596f00d27703ce09167201ba57f55be8d2f9a
- https://git.kernel.org/stable/c/b3932101c9c457148038392bc977f9b31e125a86
- https://git.kernel.org/stable/c/b7b9a8b1c303b62371698e396654d6724c79cb74
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80569.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80569
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
