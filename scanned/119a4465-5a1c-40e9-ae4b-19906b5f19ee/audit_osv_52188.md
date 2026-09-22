# [M] CVE-2021-47176

## Summary
Severity: Medium
Advisory: CVE-2021-47176
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-03-25
Source: https://osv.dev/vulnerability/CVE-2021-47176
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

s390/dasd: add missing discipline function

Fix crash with illegal operation exception in dasd_device_tasklet.
Commit b72949328869 ("s390/dasd: Prepare for additional path event handling")
renamed the verify_path function for ECKD but not for FBA and DIAG.
This leads to a panic when the path verification function is called for a
FBA or DIAG device.

Fix by defining a wrapper function for dasd_generic_verify_path().

## References
- https://git.kernel.org/stable/c/6a16810068e70959bc1df686424aa35ce05578f1
- https://git.kernel.org/stable/c/a16be88a3d7e5efcb59a15edea87a8bd369630c6
- https://git.kernel.org/stable/c/aa8579bc084673c651204f7cd0d6308a47dffc16
- https://git.kernel.org/stable/c/c0c8a8397fa8a74d04915f4d3d28cb4a5d401427
