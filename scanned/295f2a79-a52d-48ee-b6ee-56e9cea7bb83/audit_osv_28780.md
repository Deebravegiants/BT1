# [H] tpm_tis_spi: Account for SPI header when allocating TPM SPI xfer buffer

## Summary
Severity: High
Advisory: CVE-2024-36477
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-06-21
Source: https://osv.dev/vulnerability/CVE-2024-36477
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.6.0 <6.6.33, >=6.7.0 <6.9.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

tpm_tis_spi: Account for SPI header when allocating TPM SPI xfer buffer

The TPM SPI transfer mechanism uses MAX_SPI_FRAMESIZE for computing the
maximum transfer length and the size of the transfer buffer. As such, it
does not account for the 4 bytes of header that prepends the SPI data
frame. This can result in out-of-bounds accesses and was confirmed with
KASAN.

Introduce SPI_HDRSIZE to account for the header and use to allocate the
transfer buffer.

## References
- https://git.kernel.org/stable/c/1547183852dcdfcc25878db7dd3620509217b0cd
- https://git.kernel.org/stable/c/195aba96b854dd664768f382cd1db375d8181f88
- https://git.kernel.org/stable/c/de13c56f99477b56980c7e00b09c776d16b7563d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/36xxx/CVE-2024-36477.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-36477
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
