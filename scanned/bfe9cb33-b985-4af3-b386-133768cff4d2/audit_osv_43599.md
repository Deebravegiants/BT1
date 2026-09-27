# [H] drm/amd/display: Fix divide-by-zero in calculate_mcache_setting on zero viewport

## Summary
Severity: High
Advisory: CVE-2026-74449
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74449
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.11.0 <7.1.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amd/display: Fix divide-by-zero in calculate_mcache_setting on zero viewport

If a plane reaches calculate_mcache_setting with a zero-area viewport,
calculate_mcache_setting exits early with num_mcaches == 0 and
mvmpg_width/height == 0. This will cause a divide-by-zero panic and can
also cause an underflow on num_mcaches.

Fix this by changing calculate_mcache_setting to bool and adding guards
after each calculate_mcache_row_bytes call. If num_mcaches or
mvmpg_width/height is zero, return a false. Callers will propagate the
failure as a rejected mode, which prevents the panic.

(cherry picked from commit 29c0f7c655f47bcbd575ff75e58480df6ec3c9da)

## References
- https://git.kernel.org/stable/c/1f93537881fd22712732a60ad12572a3fd40c0ec
- https://git.kernel.org/stable/c/f327e389c07cfc3a2f6ff54f6214e1a52d457edc
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74449.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74449
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
