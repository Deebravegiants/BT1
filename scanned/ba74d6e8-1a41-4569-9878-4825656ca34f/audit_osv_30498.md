# [H] drm/panthor: Lock XArray when getting entries for the VM

## Summary
Severity: High
Advisory: CVE-2024-53080
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-11-19
Source: https://osv.dev/vulnerability/CVE-2024-53080
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.10.0 <6.11.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/panthor: Lock XArray when getting entries for the VM

Similar to commit cac075706f29 ("drm/panthor: Fix race when converting
group handle to group object") we need to use the XArray's internal
locking when retrieving a vm pointer from there.

v2: Removed part of the patch that was trying to protect fetching
the heap pointer from XArray, as that operation is protected by
the @pool->lock.

## References
- https://git.kernel.org/stable/c/3342f066a8e1020a6f7d1fbd6b23bfdeda473eb5
- https://git.kernel.org/stable/c/444fa5b100e5c90550d6bccfe4476efb0391b3ca
- https://project-zero.issues.chromium.org/issues/377500597
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/53xxx/CVE-2024-53080.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-53080
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
