# [H] ata: libata-sff: Ensure that we cannot write outside the allocated buffer

## Summary
Severity: High
Advisory: CVE-2025-21738
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-27
Source: https://osv.dev/vulnerability/CVE-2025-21738
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.22 <6.1.129, >=6.2.0 <6.6.78, >=6.7.0 <6.12.14, >=6.13.0 <6.13.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

ata: libata-sff: Ensure that we cannot write outside the allocated buffer

reveliofuzzing reported that a SCSI_IOCTL_SEND_COMMAND ioctl with out_len
set to 0xd42, SCSI command set to ATA_16 PASS-THROUGH, ATA command set to
ATA_NOP, and protocol set to ATA_PROT_PIO, can cause ata_pio_sector() to
write outside the allocated buffer, overwriting random memory.

While a ATA device is supposed to abort a ATA_NOP command, there does seem
to be a bug either in libata-sff or QEMU, where either this status is not
set, or the status is cleared before read by ata_sff_hsm_move().
Anyway, that is most likely a separate bug.

Looking at __atapi_pio_bytes(), it already has a safety check to ensure
that __atapi_pio_bytes() cannot write outside the allocated buffer.

Add a similar check to ata_pio_sector(), such that also ata_pio_sector()
cannot write outside the allocated buffer.

## References
- https://git.kernel.org/stable/c/0a17a9944b8d89ef03946121241870ac53ddaf45
- https://git.kernel.org/stable/c/0dd5aade301a10f4b329fa7454fdcc2518741902
- https://git.kernel.org/stable/c/6e74e53b34b6dec5a50e1404e2680852ec6768d2
- https://git.kernel.org/stable/c/a8f8cf87059ed1905c2a5c72f8b39a4f57b11b4c
- https://git.kernel.org/stable/c/d5e6e3000309359eae2a17117aa6e3c44897bf6c
- https://lists.debian.org/debian-lts-announce/2025/03/msg00028.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21738.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21738
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
