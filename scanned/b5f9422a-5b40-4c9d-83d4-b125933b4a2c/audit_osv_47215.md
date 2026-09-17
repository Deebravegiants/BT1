# [H] CVE-2016-10906

## Summary
Severity: High
Advisory: CVE-2016-10906
CVSS: 7.0 (CVSS:3.0/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-08-19
Source: https://osv.dev/vulnerability/CVE-2016-10906
Type: osv

## Details
An issue was discovered in drivers/net/ethernet/arc/emac_main.c in the Linux kernel before 4.5. A use-after-free is caused by a race condition between the functions arc_emac_tx and arc_emac_tx_clean.

## References
- https://support.f5.com/csp/article/K01993501?utm_source=f5support&amp%3Butm_medium=RSS
- https://usn.ubuntu.com/4163-1/
- https://usn.ubuntu.com/4163-2/
- http://packetstormsecurity.com/files/155212/Slackware-Security-Advisory-Slackware-14.2-kernel-Updates.html
- https://seclists.org/bugtraq/2019/Nov/11
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=c278c253f3d992c6994d08aa0efb2b6806ca396f
