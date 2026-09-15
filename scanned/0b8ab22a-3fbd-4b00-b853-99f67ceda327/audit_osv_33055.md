# [H] wifi: iwlwifi: Fix error code in iwl_op_mode_dvm_start()

## Summary
Severity: High
Advisory: CVE-2025-38656
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-08-22
Source: https://osv.dev/vulnerability/CVE-2025-38656
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: iwlwifi: Fix error code in iwl_op_mode_dvm_start()

Preserve the error code if iwl_setup_deferred_work() fails.  The current
code returns ERR_PTR(0) (which is NULL) on this path.  I believe the
missing error code potentially leads to a use after free involving
debugfs.

## References
- https://git.kernel.org/stable/c/1d068272c21d886d06526454b68368100ba0a720
- https://git.kernel.org/stable/c/991e2066f6009d3cb898413058c62dbcc92bd6d2
- https://git.kernel.org/stable/c/cf80c02a9fdb6c5bc8508beb6a0f6a1294fc32f6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38656.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38656
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
