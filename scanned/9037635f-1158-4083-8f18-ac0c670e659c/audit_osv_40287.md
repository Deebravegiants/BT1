# [H] 9p: fix access mode flags being ORed instead of replaced

## Summary
Severity: High
Advisory: CVE-2026-52906
Ecosystem: Linux
CVSS: 7.7 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-06-09
Source: https://osv.dev/vulnerability/CVE-2026-52906
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.19.0 <7.0.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

9p: fix access mode flags being ORed instead of replaced

Since commit 1f3e4142c0eb ("9p: convert to the new mount API"),
v9fs_apply_options() applies parsed mount flags with |= onto flags
already set by v9fs_session_init(). For 9P2000.L, session_init sets
V9FS_ACCESS_CLIENT as the default, so when the user mounts with
"access=user", both bits end up set. Access mode checks compare
against exact values, so having both bits set matches neither mode.

This causes v9fs_fid_lookup() to fall through to the default switch
case, using INVALID_UID (nobody/65534) instead of current_fsuid()
for all fid lookups. Root is then unable to chown or perform other
privileged operations.

Fix by clearing the access mask before applying the user's choice.

## References
- https://git.kernel.org/stable/c/b8f037e87a083291190204b959cda417aaf01058
- https://git.kernel.org/stable/c/da2346a48a5a1fed86c3fe3d73c0b60e7b3027c9
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/52xxx/CVE-2026-52906.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-52906
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
