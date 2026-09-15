# [H] net: shaper: rework the VALID marking (again)

## Summary
Severity: High
Advisory: CVE-2026-64027
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-64027
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.13.0 <6.18.34, >=6.19.0 <7.0.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: shaper: rework the VALID marking (again)

Recent commit changed the semantics from NOT_VALID to VALID.
I didn't realize that the flags are not stored atomically
with the entry in XArray. There's still a race of reader
observing a VALID mark for a slot, getting interrupted,
writer replacing the entry with a different one, reader
continuing, fetching the entry which is now a different
pointer than the pointer for which VALID was meant.

The biggest consequence of this is that we may see a UAF
since net_shaper_rollback() assumed that entries without
VALID can be freed without observing RCU.

Looks like the XArray marks are buying us nothing at this
point. Let's convert the code to an explicit valid field.
The smp_load_acquire() / smp_store_release() barriers are
marginally cleaner.

## References
- https://git.kernel.org/stable/c/2417df5e7bb4184b9d3a2988036bf2c46e594545
- https://git.kernel.org/stable/c/96ea960dd40fd55302e0fd755176f26a95e6a50c
- https://git.kernel.org/stable/c/b8d7519352ba8c6df83259295d4a3bad093cae90
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64027.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64027
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
