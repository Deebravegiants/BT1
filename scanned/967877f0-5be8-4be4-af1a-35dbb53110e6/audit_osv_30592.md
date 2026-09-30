# [H] xen: Fix the issue of resource not being properly released in xenbus_dev_probe()

## Summary
Severity: High
Advisory: CVE-2024-53198
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-12-27
Source: https://osv.dev/vulnerability/CVE-2024-53198
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.23 <5.4.287, >=5.5.0 <5.10.231, >=5.11.0 <5.15.174, >=5.16.0 <6.1.120, >=6.2.0 <6.6.64, >=6.7.0 <6.11.11, >=6.12.0 <6.12.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

xen: Fix the issue of resource not being properly released in xenbus_dev_probe()

This patch fixes an issue in the function xenbus_dev_probe(). In the
xenbus_dev_probe() function, within the if (err) branch at line 313, the
program incorrectly returns err directly without releasing the resources
allocated by err = drv->probe(dev, id). As the return value is non-zero,
the upper layers assume the processing logic has failed. However, the probe
operation was performed earlier without a corresponding remove operation.
Since the probe actually allocates resources, failing to perform the remove
operation could lead to problems.

To fix this issue, we followed the resource release logic of the
xenbus_dev_remove() function by adding a new block fail_remove before the
fail_put block. After entering the branch if (err) at line 313, the
function will use a goto statement to jump to the fail_remove block,
ensuring that the previously acquired resources are correctly released,
thus preventing the reference count leak.

This bug was identified by an experimental static analysis tool developed
by our team. The tool specializes in analyzing reference count operations
and detecting potential issues where resources are not properly managed.
In this case, the tool flagged the missing release operation as a
potential problem, which led to the development of this patch.

## References
- https://git.kernel.org/stable/c/0aa9e30b5b4af5dd504801689d6d84c584290a45
- https://git.kernel.org/stable/c/217bdce88b104269b73603b84d0ab4dd04f481bc
- https://git.kernel.org/stable/c/2f977a4c82d35d063f5fe198bbc501c4b1c5ea0e
- https://git.kernel.org/stable/c/3fc0996d2fefe61219375fd650601724b8cf2d30
- https://git.kernel.org/stable/c/804b96f8d0a02fa10b92f28b2e042f9128ed3ffc
- https://git.kernel.org/stable/c/87106169b4ce26f85561f953d13d1fd86d99b612
- https://git.kernel.org/stable/c/afc545da381ba0c651b2658966ac737032676f01
- https://git.kernel.org/stable/c/e8823e6ff313465910edea07581627d85e68d9fd
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/53xxx/CVE-2024-53198.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-53198
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
