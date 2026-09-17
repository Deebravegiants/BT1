# [M] caif_virtio: fix wrong pointer check in cfv_probe()

## Summary
Severity: Medium
Advisory: CVE-2025-21904
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-04-01
Source: https://osv.dev/vulnerability/CVE-2025-21904
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.10.0 <5.4.291, >=5.5.0 <5.10.235, >=5.11.0 <5.15.179, >=5.16.0 <6.1.131, >=6.2.0 <6.6.83, >=6.7.0 <6.12.19, >=6.13.0 <6.13.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

caif_virtio: fix wrong pointer check in cfv_probe()

del_vqs() frees virtqueues, therefore cfv->vq_tx pointer should be checked
for NULL before calling it, not cfv->vdev. Also the current implementation
is redundant because the pointer cfv->vdev is dereferenced before it is
checked for NULL.

Fix this by checking cfv->vq_tx for NULL instead of cfv->vdev before
calling del_vqs().

## References
- https://git.kernel.org/stable/c/29e0cd296c87240278e2f7ea4cf3f496b60c03af
- https://git.kernel.org/stable/c/56cddf71cce3b15b078e937fadab29962b6f6643
- https://git.kernel.org/stable/c/597c27e5f04cb50e56cc9aeda75d3e42b6b89c3e
- https://git.kernel.org/stable/c/7b5fe58959822e6cfa884327cabba6be3b01883d
- https://git.kernel.org/stable/c/8e4e08ca4cc634b337bb74bc9a70758fdeda0bcb
- https://git.kernel.org/stable/c/90d302619ee7ce5ed0c69c29c290bdccfde66418
- https://git.kernel.org/stable/c/990fff6980d0c1693d60a812f58dbf93eab0473f
- https://git.kernel.org/stable/c/a466fd7e9fafd975949e5945e2f70c33a94b1a70
- https://lists.debian.org/debian-lts-announce/2025/05/msg00030.html
- https://lists.debian.org/debian-lts-announce/2025/05/msg00045.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21904.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21904
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
