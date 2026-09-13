# [H] spi: don't unoptimize message in spi_async()

## Summary
Severity: High
Advisory: CVE-2024-42249
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-08-07
Source: https://osv.dev/vulnerability/CVE-2024-42249
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.9.0 <6.9.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

spi: don't unoptimize message in spi_async()

Calling spi_maybe_unoptimize_message() in spi_async() is wrong because
the message is likely to be in the queue and not transferred yet. This
can corrupt the message while it is being used by the controller driver.

spi_maybe_unoptimize_message() is already called in the correct place
in spi_finalize_current_message() to balance the call to
spi_maybe_optimize_message() in spi_async().

## References
- https://git.kernel.org/stable/c/8b9af6d67517ce4a0015928b3cf35bfd2b1bc1c2
- https://git.kernel.org/stable/c/c86a918b1bdba78fb155184f8d88dfba1e63335d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/42xxx/CVE-2024-42249.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-42249
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
