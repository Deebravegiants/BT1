# [M] acct: perform last write from workqueue

## Summary
Severity: Medium
Advisory: CVE-2025-21846
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-03-12
Source: https://osv.dev/vulnerability/CVE-2025-21846
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <5.4.291, >=5.5.0 <5.10.235, >=5.11.0 <5.15.179, >=5.16.0 <6.1.130, >=6.2.0 <6.6.80, >=6.7.0 <6.12.17, >=6.13.0 <6.13.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

acct: perform last write from workqueue

In [1] it was reported that the acct(2) system call can be used to
trigger NULL deref in cases where it is set to write to a file that
triggers an internal lookup. This can e.g., happen when pointing acc(2)
to /sys/power/resume. At the point the where the write to this file
happens the calling task has already exited and called exit_fs(). A
lookup will thus trigger a NULL-deref when accessing current->fs.

Reorganize the code so that the the final write happens from the
workqueue but with the caller's credentials. This preserves the
(strange) permission model and has almost no regression risk.

This api should stop to exist though.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://git.kernel.org/stable/c/56d5f3eba3f5de0efdd556de4ef381e109b973a9
- https://git.kernel.org/stable/c/5a59ced8ffc71973d42c82484a719c8f6ac8f7f7
- https://git.kernel.org/stable/c/5c928e14a2ccd99462f2351ead627b58075bb736
- https://git.kernel.org/stable/c/5d5b936cfa4b0d5670ca7420ef165a074bc008eb
- https://git.kernel.org/stable/c/5ee8da9bea70dda492d61f075658939af33d8410
- https://git.kernel.org/stable/c/8acbf4a88c6a98c8ed00afd1a7d1abcca9b4735e
- https://git.kernel.org/stable/c/a8136afca090412a36429cb6c2543c714d9c0f84
- https://git.kernel.org/stable/c/b03782ae707cc45e65242c7cddd8e28f1c22cde5
- https://lists.debian.org/debian-lts-announce/2025/05/msg00030.html
- https://lists.debian.org/debian-lts-announce/2025/05/msg00045.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21846.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21846
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
