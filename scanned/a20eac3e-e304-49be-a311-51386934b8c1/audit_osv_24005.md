# [M] dmaengine: ti: k3-udma-glue: fix memory leak when register device fail

## Summary
Severity: Medium
Advisory: CVE-2022-49860
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-05-01
Source: https://osv.dev/vulnerability/CVE-2022-49860
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.11.0 <5.15.79, >=5.16.0 <6.0.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

dmaengine: ti: k3-udma-glue: fix memory leak when register device fail

If device_register() fails, it should call put_device() to give
up reference, the name allocated in dev_set_name() can be freed
in callback function kobject_cleanup().

## References
- https://git.kernel.org/stable/c/025eab5189fc7ee223ae9b4bc49d7df196543e53
- https://git.kernel.org/stable/c/1dd27541aa2b95bde71bddd43d73f9c16d73272c
- https://git.kernel.org/stable/c/ac2b9f34f02052709aea7b34bb2a165e1853eb41
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49860.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49860
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
