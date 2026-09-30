# [H] drm/amdgpu: Add bounds checking to ib_{get,set}_value

## Summary
Severity: High
Advisory: CVE-2026-46218
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-05-28
Source: https://osv.dev/vulnerability/CVE-2026-46218
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.2.0 <6.1.175, >=6.2.0 <6.6.140, >=6.7.0 <6.12.90, >=6.13.0 <6.18.32, >=6.19.0 <7.0.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amdgpu: Add bounds checking to ib_{get,set}_value

The uvd/vce/vcn code accesses the IB at predefined offsets without
checking that the IB is large enough. Check the bounds here. The caller
is responsible for making sure it can handle arbitrary return values.

Also make the idx a uint32_t to prevent overflows causing the condition
to fail.

## References
- https://git.kernel.org/stable/c/0fb5cb556b249b2b64c0f818136c4c3e838ef53f
- https://git.kernel.org/stable/c/5da6c6430be0acb25b4242bce0323fc514d4e3cf
- https://git.kernel.org/stable/c/66085e206431ef88ce36f53c1f53d570790ccc9e
- https://git.kernel.org/stable/c/a853178d23e774adfe3a35073c375b04b3b20f7d
- https://git.kernel.org/stable/c/ee26fcf7c5cf131f0b6a732faa27d79ec61b8ec7
- https://git.kernel.org/stable/c/fec8b11b55e53ff51a741e56894fe331a516f5c6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46218.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-46218
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
