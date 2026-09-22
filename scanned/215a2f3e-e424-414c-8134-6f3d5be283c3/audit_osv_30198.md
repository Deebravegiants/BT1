# [H] drm/panthor: Fix access to uninitialized variable in tick_ctx_cleanup()

## Summary
Severity: High
Advisory: CVE-2024-50173
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-11-08
Source: https://osv.dev/vulnerability/CVE-2024-50173
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.10.0 <6.10.14, >=6.11.0 <6.11.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/panthor: Fix access to uninitialized variable in tick_ctx_cleanup()

The group variable can't be used to retrieve ptdev in our second loop,
because it points to the previously iterated list_head, not a valid
group. Get the ptdev object from the scheduler instead.

## References
- https://git.kernel.org/stable/c/282864cc5d3f144af0cdea1868ee2dc2c5110f0d
- https://git.kernel.org/stable/c/3bde05794497d5f426d4ea2ecb9868bf7721fb24
- https://git.kernel.org/stable/c/ac2ca5e5148a0d4d78ac01c2d8348d0757c7367f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50173.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50173
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
