# [M] media: venus: hfi: avoid null dereference in deinit

## Summary
Severity: Medium
Advisory: CVE-2022-49527
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49527
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.10.121, >=5.11.0 <5.15.46, >=5.13.0 <5.17.14, >=5.16.0 <5.18.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

media: venus: hfi: avoid null dereference in deinit

If venus_probe fails at pm_runtime_put_sync the error handling first
calls hfi_destroy and afterwards hfi_core_deinit. As hfi_destroy sets
core->ops to NULL, hfi_core_deinit cannot call the core_deinit function
anymore.

Avoid this null pointer derefence by skipping the call when necessary.

## References
- https://git.kernel.org/stable/c/0ed5a643b1a4a46b9b7bfba5d468c10cc30e1359
- https://git.kernel.org/stable/c/27ad46da44177a78a4a0cae6fe03906888c61aa1
- https://git.kernel.org/stable/c/86594f6af867b5165d2ba7b5a71fae3a5961e56c
- https://git.kernel.org/stable/c/9c385b961d4c378228e80f6abea8509cb67feab6
- https://git.kernel.org/stable/c/b73ed0510bb8d9647cd8e8a4c4c8772bbe545c3a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49527.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49527
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
