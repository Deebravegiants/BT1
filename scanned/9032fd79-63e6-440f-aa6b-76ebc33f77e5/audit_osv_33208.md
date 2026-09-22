# [M] spi: spi-qpic-snand: unregister ECC engine on probe error and device remove

## Summary
Severity: Medium
Advisory: CVE-2025-39893
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-10-01
Source: https://osv.dev/vulnerability/CVE-2025-39893
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.15.0 <6.16.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

spi: spi-qpic-snand: unregister ECC engine on probe error and device remove

The on-host hardware ECC engine remains registered both when
the spi_register_controller() function returns with an error
and also on device removal.

Change the qcom_spi_probe() function to unregister the engine
on the error path, and add the missing unregistering call to
qcom_spi_remove() to avoid possible use-after-free issues.

## References
- https://git.kernel.org/stable/c/1991a458528588ff34e98b6365362560d208710f
- https://git.kernel.org/stable/c/e4de48e66af17547727bb2e4b1867952817edff7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39893.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39893
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
