# [H] mm/slab: do not limit zeroing to orig_size when only red zoning is enabled

## Summary
Severity: High
Advisory: CVE-2026-64368
Ecosystem: Linux
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-25
Source: https://osv.dev/vulnerability/CVE-2026-64368
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.2.0 <6.6.145, >=6.7.0 <6.12.96, >=6.13.0 <6.18.39, >=6.19.0 <7.1.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

mm/slab: do not limit zeroing to orig_size when only red zoning is enabled

When init (zeroing) on allocation is requested, for kmalloc() we
generally have to zero the full object size even if a smaller size is
requested, in order to provide krealloc()'s __GFP_ZERO guarantees.

But if we track the requested size, krealloc() uses that information to
do the right thing, so we can zero only the requested size. With red
zoning also enabled, any extra size became part of the red zone, so it
must not be zeroed and thus we must zero only the requested size.

However the current check is imprecise, and will trigger also when only
SLAB_RED_ZONE is enabled without SLAB_STORE_USER (which enables tracking
the requested size). This means enabling red zoning alone can compromise
krealloc()'s __GFP_ZERO contract.

Fix this by using slub_debug_orig_size() instead, which is the exact
check for whether the requested size is tracked. We don't need to care
if red zoning is also enabled or not. Also update and expand the
comment accordingly.

## References
- https://git.kernel.org/stable/c/0d18ccef142f04433dfb2a0c120cf223d2b8a42c
- https://git.kernel.org/stable/c/2382971aaaef5bf85a651234c64906f59580b8be
- https://git.kernel.org/stable/c/6256899c3a34674bba6076884aedbba49fc695e4
- https://git.kernel.org/stable/c/648927ceb84021a25a0fbd5673740956f318d534
- https://git.kernel.org/stable/c/7e706d50fa119eead6376bf0ef973e8d73a96030
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64368.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64368
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
