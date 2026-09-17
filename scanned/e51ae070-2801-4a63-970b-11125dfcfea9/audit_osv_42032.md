# [C] smb: client: fix double-free in SMB2_flush() replay

## Summary
Severity: Critical
Advisory: CVE-2026-64383
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-25
Source: https://osv.dev/vulnerability/CVE-2026-64383
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.6.145, >=6.7.0 <6.12.96, >=6.8.0 <6.18.39, >=6.13.0 <7.1.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

smb: client: fix double-free in SMB2_flush() replay

SMB2_flush() keeps its response buffer bookkeeping across replay
attempts. If a replayable flush response is received and the retry then
fails before cifs_send_recv() stores a replacement response, flush_exit
will free the stale response pointer a second time.

Reinitialize resp_buftype and rsp_iov at the top of the replay loop so
cleanup only acts on response state produced by the current attempt.
This fixes a double-free without changing replay handling for successful
requests.

## References
- https://git.kernel.org/stable/c/013a9a3da46c5dabcf18f65ea6a47874ba12a15d
- https://git.kernel.org/stable/c/3407240cde132a4b72d6429a2625a09a2f78adaf
- https://git.kernel.org/stable/c/4be31c943a3a27a5a0251dbb8f5cb89059ec3d5a
- https://git.kernel.org/stable/c/6e27f40b682a5e42a2daae3ce6d96f0e0e16dedb
- https://git.kernel.org/stable/c/878757163eea684750107a31ea134c103863515d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64383.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64383
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
