# [H] drm/amdgpu/vcn3: Avoid overflow on msg bound check

## Summary
Severity: High
Advisory: CVE-2026-46237
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-05-28
Source: https://osv.dev/vulnerability/CVE-2026-46237
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amdgpu/vcn3: Avoid overflow on msg bound check

As pointed out by SDL, the previous condition may be vulnerable to
overflow.

(cherry picked from commit db00257ac9e4a51eb2515aaea161a019f7125e10)

## References
- https://git.kernel.org/stable/c/016b64a0313ea5346cf526e30c8d3e66aca10175
- https://git.kernel.org/stable/c/1936310f68c54be961de38ac539cef9b543207cb
- https://git.kernel.org/stable/c/2e43b66fceacd6e982b94f2e3f8b34edd7463396
- https://git.kernel.org/stable/c/94a2b37399807fd2ca78dc1906986c4fbd72968e
- https://git.kernel.org/stable/c/95b0f6df8d7fad2eabf265d2c3d2538ef58e4465
- https://git.kernel.org/stable/c/e6e9faba8100628990cccd13f0f044a648c303cf
- https://git.kernel.org/stable/c/e8124121b79ab5d32fa8fbbd101f7208eca9cd7d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46237.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-46237
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
