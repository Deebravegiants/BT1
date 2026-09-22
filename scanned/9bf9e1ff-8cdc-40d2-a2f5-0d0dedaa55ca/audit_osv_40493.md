# [C] xfrm: iptfs: preserve shared-frag marker in iptfs_consume_frags()

## Summary
Severity: Critical
Advisory: CVE-2026-53363
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-10
Source: https://osv.dev/vulnerability/CVE-2026-53363
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.14.0 <6.18.36, >=6.19.0 <7.0.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

xfrm: iptfs: preserve shared-frag marker in iptfs_consume_frags()

iptfs_consume_frags() transfers paged fragments from one socket buffer
to another but fails to propagate the SKBFL_SHARED_FRAG flag. This is
the same class of bug that was fixed in skb_try_coalesce() for
CVE-2026-46300: when fragments backed by read-only page-cache pages are
merged, the marker indicating their shared nature must be preserved so
that ESP can decide correctly whether in-place encryption is safe.

Apply the same two-line fix used in skb_try_coalesce() to
iptfs_consume_frags().

## References
- https://git.kernel.org/stable/c/c885d111ed9f5a0a1f3cc4e87a50db6518abaa6c
- https://git.kernel.org/stable/c/dd66f7f6e360ee82cd905517726f8e9091265de5
- https://git.kernel.org/stable/c/e9096a5a170e7ecd6467bc2e08668ec39897cda7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53363.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53363
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
