# [H] drm/exynos: vidi: use ctx->lock to protect struct vidi_context member variables related to memory alloc/free

## Summary
Severity: High
Advisory: CVE-2026-23227
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-02-18
Source: https://osv.dev/vulnerability/CVE-2026-23227
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.6.0 <5.10.253, >=5.11.0 <5.15.203, >=5.16.0 <6.1.167, >=6.2.0 <6.6.130, >=6.7.0 <6.12.77, >=6.13.0 <6.18.11, >=6.19.0 <6.19.1

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/exynos: vidi: use ctx->lock to protect struct vidi_context member variables related to memory alloc/free

Exynos Virtual Display driver performs memory alloc/free operations
without lock protection, which easily causes concurrency problem.

For example, use-after-free can occur in race scenario like this:
```
	CPU0				CPU1				CPU2
	----				----				----
  vidi_connection_ioctl()
    if (vidi->connection) // true
      drm_edid = drm_edid_alloc(); // alloc drm_edid
      ...
      ctx->raw_edid = drm_edid;
      ...
								drm_mode_getconnector()
								  drm_helper_probe_single_connector_modes()
								    vidi_get_modes()
								      if (ctx->raw_edid) // true
								        drm_edid_dup(ctx->raw_edid);
								          if (!drm_edid) // false
								          ...
				vidi_connection_ioctl()
				  if (vidi->connection) // false
				    drm_edid_free(ctx->raw_edid); // free drm_edid
				    ...
								          drm_edid_alloc(drm_edid->edid)
								            kmemdup(edid); // UAF!!
								            ...
```

To prevent these vulns, at least in vidi_context, member variables related
to memory alloc/free should be protected with ctx->lock.

## References
- https://git.kernel.org/stable/c/0cd2c155740dbd00868ac5a8ae5d14cd6b9ed385
- https://git.kernel.org/stable/c/1b24d3e8792bcc050c70e8e0dea6b49c4fc63b13
- https://git.kernel.org/stable/c/52b330799e2d6f825ae2bb74662ec1b10eb954bb
- https://git.kernel.org/stable/c/56966a4cfa925ec24edb68ab652a740a7abe2c4d
- https://git.kernel.org/stable/c/60b75407c172e1f341a8a5097c5cbc97dbbdd893
- https://git.kernel.org/stable/c/92dd1f38d7db75374dcdaf54f1d79d67bffd54e5
- https://git.kernel.org/stable/c/9e1ef9396a1899925911b1729cb65665420268df
- https://git.kernel.org/stable/c/abfdf449fb3d7b42e85a1ad1c8694b768b1582f4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23227.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-23227
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
