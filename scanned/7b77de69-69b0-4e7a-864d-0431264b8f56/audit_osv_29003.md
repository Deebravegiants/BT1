# [H] crypto: qat - validate slices count returned by FW

## Summary
Severity: High
Advisory: CVE-2024-38606
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2024-06-19
Source: https://osv.dev/vulnerability/CVE-2024-38606
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.8.0 <6.8.12, >=6.9.0 <6.9.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

crypto: qat - validate slices count returned by FW

The function adf_send_admin_tl_start() enables the telemetry (TL)
feature on a QAT device by sending the ICP_QAT_FW_TL_START message to
the firmware. This triggers the FW to start writing TL data to a DMA
buffer in memory and returns an array containing the number of
accelerators of each type (slices) supported by this HW.
The pointer to this array is stored in the adf_tl_hw_data data
structure called slice_cnt.

The array slice_cnt is then used in the function tl_print_dev_data()
to report in debugfs only statistics about the supported accelerators.
An incorrect value of the elements in slice_cnt might lead to an out
of bounds memory read.
At the moment, there isn't an implementation of FW that returns a wrong
value, but for robustness validate the slice count array returned by FW.

## References
- https://git.kernel.org/stable/c/483fd65ce29317044d1d00757e3fd23503b6b04c
- https://git.kernel.org/stable/c/9b284b915e2a5e63ca133353f8c456eff4446f82
- https://git.kernel.org/stable/c/e57ed345e2e6043629fc74aa5be051415dcc4f77
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/38xxx/CVE-2024-38606.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-38606
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
