# [H] isofs: validate Rock Ridge CE continuation extent against volume size

## Summary
Severity: High
Advisory: CVE-2026-46303
Ecosystem: Linux
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N)
Published: 2026-06-08
Source: https://osv.dev/vulnerability/CVE-2026-46303
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.19.0 <5.10.258, >=5.11.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.140, >=6.7.0 <6.12.88, >=6.13.0 <6.18.30, >=6.19.0 <7.0.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

isofs: validate Rock Ridge CE continuation extent against volume size

rock_continue() reads rs->cont_extent verbatim from the Rock Ridge CE
record and passes it to sb_bread() without checking that the block
number is within the mounted ISO 9660 volume.  commit e595447e177b
("[PATCH] rock.c: handle corrupted directories") added cont_offset
and cont_size rejection for the CE continuation but did not validate
the extent block number itself.  commit f54e18f1b831 ("isofs: Fix
infinite looping over CE entries") later capped the CE chain length
at RR_MAX_CE_ENTRIES = 32 but again left the block number unchecked.

With a crafted ISO mounted via udisks2 (desktop optical auto-mount)
or via CAP_SYS_ADMIN mount, rs->cont_extent can therefore point at
an out-of-range block or at blocks belonging to an adjacent
filesystem on the same block device.  sb_bread() on an out-of-range
block returns NULL cleanly via the block layer EIO path, so there
is no memory-safety violation.  For in-range reads of adjacent-
filesystem data, the CE buffer is parsed as Rock Ridge records and
only the text of SL sub-records reaches userspace through
readlink(), which makes the info-leak channel narrow and difficult
to exploit; still, rejecting the malformed CE outright matches the
rejection shape already present in the same function for
cont_offset and cont_size.

Add an ISOFS_SB(sb)->s_nzones bounds check to rock_continue() next
to the existing offset/size rejection, printing the same
corrupted-directory-entry notice.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://git.kernel.org/stable/c/22b36fa081f38ab397c7697f9d539211b51a0cfc
- https://git.kernel.org/stable/c/8356fb821016797f5677cbeee5ddc0d32a95b4be
- https://git.kernel.org/stable/c/a36d990f591320e9dd379ab30063ebfe91d47e1f
- https://git.kernel.org/stable/c/bf1bc673c587f5ef7e9c09b94aea7c5a7847d4d9
- https://git.kernel.org/stable/c/c9b37c8b73f6368e4750e5ccb0632c380b43c6e5
- https://git.kernel.org/stable/c/d582e12378bc1637f337622feef762f53c43fd57
- https://git.kernel.org/stable/c/e69da8eeab74b4f4505024c38a17bce060fe7df8
- https://git.kernel.org/stable/c/ef048470c90bc8c1b8318bb2ce329da9ef64b9fe
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46303.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-46303
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
