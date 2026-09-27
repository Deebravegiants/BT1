# [H] spi: cadence-qspi: fix pointer reference in runtime PM hooks

## Summary
Severity: High
Advisory: CVE-2024-26807
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-04-04
Source: https://osv.dev/vulnerability/CVE-2024-26807
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.1.140, >=6.2.0 <6.6.21, >=6.4.0 <6.7.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

Both cadence-quadspi ->runtime_suspend() and ->runtime_resume()
implementations start with:

	struct cqspi_st *cqspi = dev_get_drvdata(dev);
	struct spi_controller *host = dev_get_drvdata(dev);

This obviously cannot be correct, unless "struct cqspi_st" is the
first member of " struct spi_controller", or the other way around, but
it is not the case. "struct spi_controller" is allocated by
devm_spi_alloc_host(), which allocates an extra amount of memory for
private data, used to store "struct cqspi_st".

The ->probe() function of the cadence-quadspi driver then sets the
device drvdata to store the address of the "struct cqspi_st"
structure. Therefore:

	struct cqspi_st *cqspi = dev_get_drvdata(dev);

is correct, but:

	struct spi_controller *host = dev_get_drvdata(dev);

is not, as it makes "host" point not to a "struct spi_controller" but
to the same "struct cqspi_st" structure as above.

This obviously leads to bad things (memory corruption, kernel crashes)
directly during ->probe(), as ->probe() enables the device using PM
runtime, leading the ->runtime_resume() hook being called, which in
turns calls spi_controller_resume() with the wrong pointer.

This has at least been reported [0] to cause a kernel crash, but the
exact behavior will depend on the memory contents.

[0] https://lore.kernel.org/all/20240226121803.5a7r5wkpbbowcxgx@dhruva/

This issue potentially affects all platforms that are currently using
the cadence-quadspi driver.

## References
- https://git.kernel.org/stable/c/03f1573c9587029730ca68503f5062105b122f61
- https://git.kernel.org/stable/c/2c914aac9522f6e93822c18dff233d3e92399c81
- https://git.kernel.org/stable/c/32ce3bb57b6b402de2aec1012511e7ac4e7449dc
- https://git.kernel.org/stable/c/34e1d5c4407c78de0e3473e1fbf8fb74dbe66d03
- https://lists.debian.org/debian-lts-announce/2025/08/msg00010.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26807.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26807
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
