# [H] virtio: packed: fix unmap leak for indirect desc table

## Summary
Severity: High
Advisory: CVE-2024-27066
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-01
Source: https://osv.dev/vulnerability/CVE-2024-27066
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.6.0 <6.6.23, >=6.7.0 <6.7.11, >=6.8.0 <6.8.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

virtio: packed: fix unmap leak for indirect desc table

When use_dma_api and premapped are true, then the do_unmap is false.

Because the do_unmap is false, vring_unmap_extra_packed is not called by
detach_buf_packed.

  if (unlikely(vq->do_unmap)) {
                curr = id;
                for (i = 0; i < state->num; i++) {
                        vring_unmap_extra_packed(vq,
                                                 &vq->packed.desc_extra[curr]);
                        curr = vq->packed.desc_extra[curr].next;
                }
  }

So the indirect desc table is not unmapped. This causes the unmap leak.

So here, we check vq->use_dma_api instead. Synchronously, dma info is
updated based on use_dma_api judgment

This bug does not occur, because no driver use the premapped with
indirect.

## References
- https://git.kernel.org/stable/c/51bacd9d29bf98c3ebc65e4a0477bb86306b4140
- https://git.kernel.org/stable/c/75450ff8c6fe8755bf5b139b238eaf9739cfd64e
- https://git.kernel.org/stable/c/d5c0ed17fea60cca9bc3bf1278b49ba79242bbcd
- https://git.kernel.org/stable/c/e142169aca5546ae6619c39a575cda8105362100
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/27xxx/CVE-2024-27066.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-27066
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
