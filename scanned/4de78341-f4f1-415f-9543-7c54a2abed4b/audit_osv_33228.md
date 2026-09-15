# [M] spi: microchip-core-qspi: stop checking viability of op->max_freq in supports_op callback

## Summary
Severity: Medium
Advisory: CVE-2025-39921
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-10-01
Source: https://osv.dev/vulnerability/CVE-2025-39921
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.14.0 <6.16.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

spi: microchip-core-qspi: stop checking viability of op->max_freq in supports_op callback

In commit 13529647743d9 ("spi: microchip-core-qspi: Support per spi-mem
operation frequency switches") the logic for checking the viability of
op->max_freq in mchp_coreqspi_setup_clock() was copied into
mchp_coreqspi_supports_op(). Unfortunately, op->max_freq is not valid
when this function is called during probe but is instead zero.
Accordingly, baud_rate_val is calculated to be INT_MAX due to division
by zero, causing probe of the attached memory device to fail.

Seemingly spi-microchip-core-qspi was the only driver that had such a
modification made to its supports_op callback when the per_op_freq
capability was added, so just remove it to restore prior functionality.

## References
- https://git.kernel.org/stable/c/89e7353f522f5cf70cb48c01ce2dcdcb275b8022
- https://git.kernel.org/stable/c/ac8a13f35d5b8996582b3f97b924838a5c570c18
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39921.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39921
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
