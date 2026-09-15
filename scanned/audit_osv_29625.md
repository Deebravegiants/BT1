# [C] nvme: move stopping keep-alive into nvme_uninit_ctrl()

## Summary
Severity: Critical
Advisory: CVE-2024-45013
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-09-11
Source: https://osv.dev/vulnerability/CVE-2024-45013
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.7.0 <6.10.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

nvme: move stopping keep-alive into nvme_uninit_ctrl()

Commit 4733b65d82bd ("nvme: start keep-alive after admin queue setup")
moves starting keep-alive from nvme_start_ctrl() into
nvme_init_ctrl_finish(), but don't move stopping keep-alive into
nvme_uninit_ctrl(), so keep-alive work can be started and keep pending
after failing to start controller, finally use-after-free is triggered if
nvme host driver is unloaded.

This patch fixes kernel panic when running nvme/004 in case that connection
failure is triggered, by moving stopping keep-alive into nvme_uninit_ctrl().

This way is reasonable because keep-alive is now started in
nvme_init_ctrl_finish().

## References
- https://git.kernel.org/stable/c/4101af98ab573554c4225e328d506fec2a74bc54
- https://git.kernel.org/stable/c/a54a93d0e3599b05856971734e15418ac551a14c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/45xxx/CVE-2024-45013.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-45013
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
