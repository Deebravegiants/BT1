# [H] scsi: fnic: Fix crash in fnic_wq_cmpl_handler when FDMI times out

## Summary
Severity: High
Advisory: CVE-2025-38238
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-07-09
Source: https://osv.dev/vulnerability/CVE-2025-38238
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.14.0 <6.15.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

scsi: fnic: Fix crash in fnic_wq_cmpl_handler when FDMI times out

When both the RHBA and RPA FDMI requests time out, fnic reuses a frame to
send ABTS for each of them. On send completion, this causes an attempt to
free the same frame twice that leads to a crash.

Fix crash by allocating separate frames for RHBA and RPA, and modify ABTS
logic accordingly.

Tested by checking MDS for FDMI information.

Tested by using instrumented driver to:

 - Drop PLOGI response
 - Drop RHBA response
 - Drop RPA response
 - Drop RHBA and RPA response
 - Drop PLOGI response + ABTS response
 - Drop RHBA response + ABTS response
 - Drop RPA response + ABTS response
 - Drop RHBA and RPA response + ABTS response for both of them

## References
- https://git.kernel.org/stable/c/09679e9abedfbc5a2590759a1a7893c1c26e6044
- https://git.kernel.org/stable/c/a35b29bdedb4d2ae3160d4d6684a6f1ecd9ca7c2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38238.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38238
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
