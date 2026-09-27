# [H] iio: adc: xilinx-ams: fix out-of-bounds channel lookup in event handling

## Summary
Severity: High
Advisory: CVE-2026-72480
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72480
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.17.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

iio: adc: xilinx-ams: fix out-of-bounds channel lookup in event handling

ams_event_to_channel() may return a pointer past the end of
dev->channels when no matching scan_index is found. This can lead
to invalid memory access in ams_handle_event().

Add a bounds check in ams_event_to_channel() and return NULL when
no channel is found. Also guard the caller to safely handle this
case.

## References
- https://git.kernel.org/stable/c/116d1f8805ae2daadbac89d24da4c0da50b9edae
- https://git.kernel.org/stable/c/1d24f14e049fdd769146dda026496ed23b397ed9
- https://git.kernel.org/stable/c/3c374d33f1338dbb5676919c5194caa9c5aa1631
- https://git.kernel.org/stable/c/947eb6f0a274f8b15a0248051a65b069effd5057
- https://git.kernel.org/stable/c/94d158985b6ea011bdc26186f42d662a156da6cb
- https://git.kernel.org/stable/c/9ac3675bf875792dced45efbf47116719a7c097b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72480.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72480
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
