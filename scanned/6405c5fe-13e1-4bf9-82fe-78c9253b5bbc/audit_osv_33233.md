# [H] ceph: fix race condition validating r_parent before applying state

## Summary
Severity: High
Advisory: CVE-2025-39927
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-01
Source: https://osv.dev/vulnerability/CVE-2025-39927
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.34 <6.12.48, >=6.13.0 <6.16.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

ceph: fix race condition validating r_parent before applying state

Add validation to ensure the cached parent directory inode matches the
directory info in MDS replies. This prevents client-side race conditions
where concurrent operations (e.g. rename) cause r_parent to become stale
between request initiation and reply processing, which could lead to
applying state changes to incorrect directory inodes.

[ idryomov: folded a kerneldoc fixup and a follow-up fix from Alex to
  move CEPH_CAP_PIN reference when r_parent is updated:

  When the parent directory lock is not held, req->r_parent can become
  stale and is updated to point to the correct inode.  However, the
  associated CEPH_CAP_PIN reference was not being adjusted.  The
  CEPH_CAP_PIN is a reference on an inode that is tracked for
  accounting purposes.  Moving this pin is important to keep the
  accounting balanced. When the pin was not moved from the old parent
  to the new one, it created two problems: The reference on the old,
  stale parent was never released, causing a reference leak.
  A reference for the new parent was never acquired, creating the risk
  of a reference underflow later in ceph_mdsc_release_request().  This
  patch corrects the logic by releasing the pin from the old parent and
  acquiring it for the new parent when r_parent is switched.  This
  ensures reference accounting stays balanced. ]

## References
- https://git.kernel.org/stable/c/15f519e9f883b316d86e2bb6b767a023aafd9d83
- https://git.kernel.org/stable/c/2bfe45987eb346e299d9f763f9cd05f77011519f
- https://git.kernel.org/stable/c/db378e6f83ec705c6091c65d482d555edc2b0a72
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39927.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39927
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
