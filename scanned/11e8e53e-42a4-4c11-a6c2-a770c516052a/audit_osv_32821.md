# [H] vhost-scsi: protect vq->log_used with vq->mutex

## Summary
Severity: High
Advisory: CVE-2025-38074
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2025-06-18
Source: https://osv.dev/vulnerability/CVE-2025-38074
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.6.0 <5.10.240, >=5.11.0 <5.15.189, >=5.16.0 <6.1.146, >=6.2.0 <6.6.93, >=6.7.0 <6.12.31, >=6.13.0 <6.14.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

vhost-scsi: protect vq->log_used with vq->mutex

The vhost-scsi completion path may access vq->log_base when vq->log_used is
already set to false.

    vhost-thread                       QEMU-thread

vhost_scsi_complete_cmd_work()
-> vhost_add_used()
   -> vhost_add_used_n()
      if (unlikely(vq->log_used))
                                      QEMU disables vq->log_used
                                      via VHOST_SET_VRING_ADDR.
                                      mutex_lock(&vq->mutex);
                                      vq->log_used = false now!
                                      mutex_unlock(&vq->mutex);

				      QEMU gfree(vq->log_base)
        log_used()
        -> log_write(vq->log_base)

Assuming the VMM is QEMU. The vq->log_base is from QEMU userpace and can be
reclaimed via gfree(). As a result, this causes invalid memory writes to
QEMU userspace.

The control queue path has the same issue.

## References
- https://git.kernel.org/stable/c/59614c5acf6688f7af3c245d359082c0e9e53117
- https://git.kernel.org/stable/c/80cf68489681c165ded460930e391b1eb37b5f6f
- https://git.kernel.org/stable/c/8312a1ccff1566f375191a89b9ba71b6eb48a8cd
- https://git.kernel.org/stable/c/bd8c9404e44adb9f6219c09b3409a61ab7ce3427
- https://git.kernel.org/stable/c/c0039e3afda29be469d29b3013d7f9bdee136834
- https://git.kernel.org/stable/c/ca85c2d0db5f8309832be45858b960d933c2131c
- https://git.kernel.org/stable/c/f591cf9fce724e5075cc67488c43c6e39e8cbe27
- https://lists.debian.org/debian-lts-announce/2025/10/msg00007.html
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38074.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38074
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
