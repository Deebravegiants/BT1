# [H] ntfs: ->d_compare() must not block

## Summary
Severity: High
Advisory: CVE-2026-43245
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-05-06
Source: https://osv.dev/vulnerability/CVE-2026-43245
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.2.0 <6.6.141, >=6.7.0 <6.12.91, >=6.13.0 <6.18.16, >=6.19.0 <6.19.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

ntfs: ->d_compare() must not block

... so don't use __getname() there.  Switch it (and ntfs_d_hash(), while
we are at it) to kmalloc(PATH_MAX, GFP_NOWAIT).  Yes, ntfs_d_hash()
almost certainly can do with smaller allocations, but let ntfs folks
deal with that - keep the allocation size as-is for now.

Stop abusing names_cachep in ntfs, period - various uses of that thing
in there have nothing to do with pathnames; just use k[mz]alloc() and
be done with that.  For now let's keep sizes as-in, but AFAICS none of
the users actually want PATH_MAX.

## References
- https://git.kernel.org/stable/c/02ecc0978c459fd90bb24b2a946dd16d43e68fe5
- https://git.kernel.org/stable/c/142c444a395f4d26055c8a4473e228bb86283f1e
- https://git.kernel.org/stable/c/1be7ca86ce1794d966fda5d82181bc978b150fbc
- https://git.kernel.org/stable/c/ca2a04e84af79596e5cd9cfe697d5122ec39c8ce
- https://git.kernel.org/stable/c/fb4b1f969ba01fa1d4088467a02fc1e5f0806710
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43245.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43245
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
