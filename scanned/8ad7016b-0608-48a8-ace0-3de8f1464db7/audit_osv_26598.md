# [M] media: mdp3: Fix resource leaks in of_find_device_by_node

## Summary
Severity: Medium
Advisory: CVE-2023-53385
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-18
Source: https://osv.dev/vulnerability/CVE-2023-53385
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.1.0 <6.1.55, >=6.2.0 <6.5.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

media: mdp3: Fix resource leaks in of_find_device_by_node

Use put_device to release the object get through of_find_device_by_node,
avoiding resource leaks.

## References
- https://git.kernel.org/stable/c/35ca8ce495366909b4c2e701d1356570dd40c4e2
- https://git.kernel.org/stable/c/8ba9d91c8f21f070af2049f114c206a8f2d5c71e
- https://git.kernel.org/stable/c/fa481125bc4ca8edc1a4c62fe53486ac9a817593
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53385.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53385
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
