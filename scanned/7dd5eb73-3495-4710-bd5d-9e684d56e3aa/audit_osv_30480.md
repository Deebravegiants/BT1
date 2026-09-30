# [H] wifi: iwlwifi: mvm: Fix response handling in iwl_mvm_send_recovery_cmd()

## Summary
Severity: High
Advisory: CVE-2024-53059
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:H)
Published: 2024-11-19
Source: https://osv.dev/vulnerability/CVE-2024-53059
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.1.0 <5.4.285, >=5.5.0 <5.10.229, >=5.11.0 <5.15.171, >=5.16.0 <6.1.116, >=6.2.0 <6.6.60, >=6.7.0 <6.11.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: iwlwifi: mvm: Fix response handling in iwl_mvm_send_recovery_cmd()

1. The size of the response packet is not validated.
2. The response buffer is not freed.

Resolve these issues by switching to iwl_mvm_send_cmd_status(),
which handles both size validation and frees the buffer.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://cert-portal.siemens.com/productcert/html/ssa-355557.html
- https://git.kernel.org/stable/c/07a6e3b78a65f4b2796a8d0d4adb1a15a81edead
- https://git.kernel.org/stable/c/3eb986c64c6bfb721950f9666a3b723cf65d043f
- https://git.kernel.org/stable/c/3f45d590ccbae6dfd6faef54efe74c30bd85d3da
- https://git.kernel.org/stable/c/45a628911d3c68e024eed337054a0452b064f450
- https://git.kernel.org/stable/c/64d63557ded6ff3ce72b18ab87a6c4b1b652161c
- https://git.kernel.org/stable/c/9480c3045f302f43f9910d2d556d6cf5a62c1822
- https://git.kernel.org/stable/c/9c98ee7ea463a838235e7a0e35851b38476364f2
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/53xxx/CVE-2024-53059.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-53059
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
