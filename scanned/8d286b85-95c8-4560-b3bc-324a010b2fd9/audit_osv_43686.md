# [H] vhost: reset the vring metadata cache on vring reconfiguration

## Summary
Severity: High
Advisory: CVE-2026-74580
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-08-21
Source: https://osv.dev/vulnerability/CVE-2026-74580
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.11.0 <5.10.265, >=5.11.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.152, >=6.7.0 <6.12.104, >=6.13.0 <6.18.45, >=6.19.0 <7.1.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

vhost: reset the vring metadata cache on vring reconfiguration

vq->meta_iotlb[] caches the vhost_iotlb_map that backs each vring
metadata region, and iotlb_access_ok() returns early on a cache hit,
taking the hit as proof that the region has already been validated:

	if (vhost_vq_meta_fetch(vq, addr, len, type))
		return true;

The cache is reset on VHOST_IOTLB_UPDATE and VHOST_IOTLB_INVALIDATE, on
device IOTLB (re)initialisation and on vq reset, but not when
VHOST_SET_VRING_ADDR replaces vq->desc, vq->avail and vq->used, nor when
VHOST_SET_VRING_NUM changes the region sizes.

With a device IOTLB attached both ioctls are accepted while the vq is
live, and neither validates the addresses at ioctl time: vq_access_ok()
and vq_log_used_access_ok() return true early because the addresses are
GIOVAs, deferring validation to prefetch time.  Once the cache has been
populated that deferred validation no longer runs -- vq_meta_prefetch()
hits the stale entry and returns true -- and vhost_vq_meta_fetch() keeps
translating through the old mapping as

	map->addr + addr - map->start

for an address the mapping no longer covers.  vhost_copy_to_user() and
vhost_copy_from_user() consume the result with __copy_to_user() and
__copy_from_user(), which do not check it either, so a subsequent used
ring update or descriptor fetch accesses memory outside the region the
IOTLB actually maps.

Reset the metadata cache whenever the vring is reconfigured, so the new
addresses are pushed back through iotlb_access_ok()'s slow path.

## References
- https://git.kernel.org/stable/c/13fa6f32a56a386a82bd7451644c494beed034af
- https://git.kernel.org/stable/c/5224bd37e37d36076a550d99b2aebba33939fd95
- https://git.kernel.org/stable/c/54617e9119be2eb728ecdd8d977b99c99d4c498a
- https://git.kernel.org/stable/c/6fa3e9b1fe856259555a7e22f3f3082e7827fd9b
- https://git.kernel.org/stable/c/b70ebe0bba254e093dd5fd4c0c170941ce83eb85
- https://git.kernel.org/stable/c/cf363a7a02ce132ef1f58084fdb13e1a3b7da7e7
- https://git.kernel.org/stable/c/de845981da67a6b049080c87e605130b0c30adc5
- https://git.kernel.org/stable/c/f1e21108e3ddfcce62f6cad4ebd7b5674543c9e6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74580.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74580
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
