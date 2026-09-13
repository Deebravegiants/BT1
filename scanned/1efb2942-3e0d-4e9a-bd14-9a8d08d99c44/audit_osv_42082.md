# [H] hwrng: virtio: clamp device-reported used.len at copy_data()

## Summary
Severity: High
Advisory: CVE-2026-64456
Ecosystem: Linux
CVSS: 7.7 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-07-25
Source: https://osv.dev/vulnerability/CVE-2026-64456
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.26 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.96, >=6.13.0 <6.18.39, >=6.19.0 <7.1.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

hwrng: virtio: clamp device-reported used.len at copy_data()

random_recv_done() stores the device-reported used.len directly into
vi->data_avail.  copy_data() then indexes vi->data[] using
vi->data_idx (advanced by previous copy_data() calls) and issues a
memcpy() without re-validating either value against the posted
buffer size sizeof(vi->data) (SMP_CACHE_BYTES bytes, typically 32
or 64).

A malicious or buggy virtio-rng backend can set used.len beyond
sizeof(vi->data), steering the memcpy() past the end of the inline
array into adjacent kmalloc-1k slab bytes.  hwrng_fillfn() mixes
those bytes into the guest RNG, and guest root can also observe
them directly via /dev/hwrng.

Concrete impact is inside the guest:

 - Memory-safety / hardening: any virtio-rng backend that
   over-reports used.len causes the driver to read past vi->data
   into unrelated slab contents.  hwrng_fillfn() is a kernel thread
   that runs as soon as the device is probed; no guest userspace
   interaction is required to first-trigger the OOB.

 - Cross-boundary leak (confidential-compute threat model): a
   malicious hypervisor cooperating with a malicious or compromised
   guest root userspace can use /dev/hwrng as a leak channel for
   guest-kernel heap data.  The host sets a large used.len, guest
   root reads /dev/hwrng, and the returned bytes contain guest
   kernel slab contents that were adjacent to vi->data.  In
   practice, confidential-compute guests (SEV-SNP, TDX) usually
   disable virtio-rng entirely, so this path is narrow, but the
   fix is still worth carrying because the underlying
   memory-safety bug contaminates the guest RNG on any host.

KASAN confirms the OOB on a 7.1-rc4 guest whose virtio-rng backend
has been patched to report used.len = 0x10000:

  BUG: KASAN: slab-out-of-bounds in virtio_read+0x394/0x5d0
  Read of size 64 at addr ffff88800ae0ba20 by task hwrng/52
  Call Trace:
   __asan_memcpy+0x23/0x60
   virtio_read+0x394/0x5d0
   hwrng_fillfn+0xb2/0x470
   kthread+0x2cc/0x3a0
  Allocated by task 1:
   probe_common+0xa5/0x660
   virtio_dev_probe+0x549/0xbc0
  The buggy address belongs to the object at ffff88800ae0b800
   which belongs to the cache kmalloc-1k of size 1024
  The buggy address is located 0 bytes to the right of
   allocated 544-byte region [ffff88800ae0b800, ffff88800ae0ba20)

Same class of bug as commit c04db81cd028 ("net/9p: Fix buffer
overflow in USB transport layer"), which hardened
usb9pfs_rx_complete() against unchecked device-reported length in
the USB 9p transport.

With the clamp at point of use and array_index_nospec() in place,
the same harness boots cleanly: copy_data() returns zero for the
bogus report, the device-supplied bytes after data_idx are
discarded, and the driver issues a fresh request.

## References
- https://git.kernel.org/stable/c/285e17c44e3873a73460f294acbd64018ff64385
- https://git.kernel.org/stable/c/2e788948ff2a13358a303af112497a63201c5739
- https://git.kernel.org/stable/c/3aa3e89cf80721c8d382b4c1a2b70a0449dad4a5
- https://git.kernel.org/stable/c/63335e7b638ae70028ae285bb95153874a8bc852
- https://git.kernel.org/stable/c/81dd21b5f0c299cc7b5bf84f04a61938559d20e6
- https://git.kernel.org/stable/c/92d5736a62040ec1cfff23ea57e6599301690ad5
- https://git.kernel.org/stable/c/e3046eeada299f917a8ad883af4434bfb86556b1
- https://git.kernel.org/stable/c/fde19b0d4eeabae042519313c843fe6f27d41e9d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64456.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64456
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
