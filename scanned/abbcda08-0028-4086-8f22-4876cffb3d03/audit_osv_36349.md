# [H] wifi: iwlwifi: mld: cancel mlo_scan_start_wk

## Summary
Severity: High
Advisory: CVE-2026-23185
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-02-14
Source: https://osv.dev/vulnerability/CVE-2026-23185
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.17.0 <6.18.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: iwlwifi: mld: cancel mlo_scan_start_wk

mlo_scan_start_wk is not canceled on disconnection. In fact, it is not
canceled anywhere except in the restart cleanup, where we don't really
have to.

This can cause an init-after-queue issue: if, for example, the work was
queued and then drv_change_interface got executed.

This can also cause use-after-free: if the work is executed after the
vif is freed.

## References
- https://git.kernel.org/stable/c/5ff641011ab7fb63ea101251087745d9826e8ef5
- https://git.kernel.org/stable/c/9b9f52f052f4953fecd2190ae2dde3aa76d10962
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-23185.json
- https://access.redhat.com/security/cve/CVE-2026-23185
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23185.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-23185
- https://bugzilla.redhat.com/show_bug.cgi?id=2439925
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
