# [H] dm: clear cloned request bio pointer when last clone bio completes

## Summary
Severity: High
Advisory: CVE-2026-43278
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-06
Source: https://osv.dev/vulnerability/CVE-2026-43278
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.1.0 <6.1.165, >=6.2.0 <6.6.128, >=6.7.0 <6.12.75, >=6.13.0 <6.18.16, >=6.19.0 <6.19.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

dm: clear cloned request bio pointer when last clone bio completes

Stale rq->bio values have been observed to cause double-initialization of
cloned bios in request-based device-mapper targets, leading to
use-after-free and double-free scenarios.

One such case occurs when using dm-multipath on top of a PCIe NVMe
namespace, where cloned request bios are freed during
blk_complete_request(), but rq->bio is left intact. Subsequent clone
teardown then attempts to free the same bios again via
blk_rq_unprep_clone().

The resulting double-free path looks like:

  nvme_pci_complete_batch()
    nvme_complete_batch()
      blk_mq_end_request_batch()
        blk_complete_request()        // called on a DM clone request
          bio_endio()                 // first free of all clone bios
          ...
        rq->end_io()                  // end_clone_request()
          dm_complete_request(tio->orig)
            dm_softirq_done()
              dm_done()
                dm_end_request()
                  blk_rq_unprep_clone()  // second free of clone bios

Fix this by clearing the clone request's bio pointer when the last cloned
bio completes, ensuring that later teardown paths do not attempt to free
already-released bios.

## References
- https://git.kernel.org/stable/c/7daf279c674d515fb22a727a7bbc92aeb35c5442
- https://git.kernel.org/stable/c/83d72091804600ead96dc9e9f518ea56cb4942f6
- https://git.kernel.org/stable/c/8d9ddad561136f7e6a9346767bf97b4d79e38e67
- https://git.kernel.org/stable/c/b1c1a2637ebd675aa2d71fee8c70da8791d73850
- https://git.kernel.org/stable/c/e2e738e8dfbbf83bd2bae0467ec4420cc52da42a
- https://git.kernel.org/stable/c/fb8a6c18fb9a6561f7a15b58b272442b77a242dd
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43278.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43278
- https://git.kernel.org/stable/c/3d746b639be4b4f5cd8ce2b06aa52dc443f50edc
- https://git.kernel.org/stable/c/9a95b98202113045bc1a5bcb30388a500f25e050
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
