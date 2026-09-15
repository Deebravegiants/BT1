# [H] accel/amdxdna: Use caller client for debug BO sync

## Summary
Severity: High
Advisory: CVE-2026-72090
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72090
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

accel/amdxdna: Use caller client for debug BO sync

amdxdna_drm_sync_bo_ioctl() looks up args->handle in the ioctl caller's
drm_file. For SYNC_DIRECT_FROM_DEVICE, it then calls
amdxdna_hwctx_sync_debug_bo(), but passes abo->client.

amdxdna_hwctx_sync_debug_bo() uses the passed client both as the handle
namespace for debug_bo_hdl and as the owner of the hardware context xarray.
Those must match the file that supplied args->handle. The BO's stored
client pointer is object state, not the ioctl context.

Pass filp->driver_priv instead, matching the original handle lookup.

## References
- https://git.kernel.org/stable/c/216e43d93dd49ec253052741aa476e51a8c54cd8
- https://git.kernel.org/stable/c/7caf2a2351d4053075670ff3e26a6815da0a9e1e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72090.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72090
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
