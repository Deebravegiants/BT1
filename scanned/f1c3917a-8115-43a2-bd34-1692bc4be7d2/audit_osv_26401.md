# [H] arm64: dts: qcom: sc7280: Mark PCIe controller as cache coherent

## Summary
Severity: High
Advisory: CVE-2023-53043
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-05-02
Source: https://osv.dev/vulnerability/CVE-2023-53043
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.16.0 <6.1.22, >=6.2.0 <6.2.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

arm64: dts: qcom: sc7280: Mark PCIe controller as cache coherent

If the controller is not marked as cache coherent, then kernel will
try to ensure coherency during dma-ops and that may cause data corruption.
So, mark the PCIe node as dma-coherent as the devices on PCIe bus are
cache coherent.

## References
- https://git.kernel.org/stable/c/267b899375bf38944d915c9654d6eb434edad0ce
- https://git.kernel.org/stable/c/8a63441e83724fee1ef3fd37b237d40d90780766
- https://git.kernel.org/stable/c/e43bba938e2c9104bb4f8bc417ac4d7bb29755e1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53043.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53043
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
