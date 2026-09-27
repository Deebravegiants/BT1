# [C] smb: client: protect tc_count increment in smb2_find_smb_sess_tcon_unlocked()

## Summary
Severity: Critical
Advisory: CVE-2026-64136
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-64136
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.6.142, >=6.7.0 <6.12.92, >=6.13.0 <6.18.34, >=6.19.0 <7.0.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

smb: client: protect tc_count increment in smb2_find_smb_sess_tcon_unlocked()

Commit 96c4af418586 ("cifs: Fix locking usage for tcon fields")
refactored cifs code to change cifs_tcp_ses_lock for tc_lock around
tc_count changes.

There was missing lock around tc_count increment inside
smb2_find_smb_sess_tcon_unlocked().

## References
- https://git.kernel.org/stable/c/13fb413ae22a37c69341918a6d651d19a9b0b9b7
- https://git.kernel.org/stable/c/4d8690dace005a38e6dbde9ecce2da3ad85c7c41
- https://git.kernel.org/stable/c/7df1df6f40c0720d30206aa35c0343b962350e0d
- https://git.kernel.org/stable/c/bf4ebdb19ff9b3cdf992b50715fe61633327416a
- https://git.kernel.org/stable/c/e374f4e496fef8168784f93a4477d67be34485fd
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64136.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64136
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
