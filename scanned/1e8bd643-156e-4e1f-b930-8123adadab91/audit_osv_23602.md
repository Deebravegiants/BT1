# [H] drm/amd/display: Fix double free during GPU reset on DC streams

## Summary
Severity: High
Advisory: CVE-2022-49203
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49203
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.17.0 <5.17.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amd/display: Fix double free during GPU reset on DC streams

[Why]
The issue only occurs during the GPU reset code path.

We first backup the current state prior to commiting 0 streams
internally from DM to DC. This state backup contains valid link
encoder assignments.

DC will clear the link encoder assignments as part of current state
(but not the backup, since it was a copied before the commit) and
free the extra stream reference it held.

DC requires that the link encoder assignments remain cleared/invalid
prior to commiting. Since the backup still has valid assignments we
call the interface post reset to clear them. This routine also
releases the extra reference that the link encoder interface held -
resulting in a double free (and eventually a NULL pointer dereference).

[How]
We'll have to do a full DC commit anyway after GPU reset because
the stream count previously went to 0.

We don't need to retain the assignment that we had backed up, so
just copy off of the now clean current state assignment after the
reset has occcurred with the new link_enc_cfg_copy() interface.

## References
- https://git.kernel.org/stable/c/32685b32d825ca08c5dec826477332df886c4743
- https://git.kernel.org/stable/c/bbfcdd6289ba6f00f0cd7d496946dce9f6c600ac
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49203.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49203
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
