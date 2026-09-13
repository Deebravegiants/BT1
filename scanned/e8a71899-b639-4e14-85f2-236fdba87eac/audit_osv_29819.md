# [H] net: microchip: vcap: Fix use-after-free error in kunit test

## Summary
Severity: High
Advisory: CVE-2024-46831
Ecosystem: Linux
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-09-27
Source: https://osv.dev/vulnerability/CVE-2024-46831
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.2.0 <6.6.51, >=6.7.0 <6.10.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: microchip: vcap: Fix use-after-free error in kunit test

This is a clear use-after-free error. We remove it, and rely on checking
the return code of vcap_del_rule.

## References
- https://git.kernel.org/stable/c/a3c1e45156ad39f225cd7ddae0f81230a3b1e657
- https://git.kernel.org/stable/c/b0804c286ccfcf5f5c004d5bf8a54c0508b5e86b
- https://git.kernel.org/stable/c/f7fe95f40c85311c98913fe6ae2c56adb7f767a7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/46xxx/CVE-2024-46831.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-46831
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
