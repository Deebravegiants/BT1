# [H] Bluetooth: hci_qca: Use del_timer_sync() before freeing

## Summary
Severity: High
Advisory: CVE-2022-49555
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49555
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.3.0 <5.10.120, >=5.11.0 <5.15.45, >=5.16.0 <5.17.13, >=5.18.0 <5.18.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: hci_qca: Use del_timer_sync() before freeing

While looking at a crash report on a timer list being corrupted, which
usually happens when a timer is freed while still active. This is
commonly triggered by code calling del_timer() instead of
del_timer_sync() just before freeing.

One possible culprit is the hci_qca driver, which does exactly that.

Eric mentioned that wake_retrans_timer could be rearmed via the work
queue, so also move the destruction of the work queue before
del_timer_sync().

## References
- https://git.kernel.org/stable/c/2717654ae022e6ea959a4b7b762702fe1a4690c2
- https://git.kernel.org/stable/c/37d17f63d085d601011964ade7371aeebeb6ed4b
- https://git.kernel.org/stable/c/4989bb03342941f2b730b37dfa38bce27b543661
- https://git.kernel.org/stable/c/72ef98445aca568a81c2da050532500a8345ad3a
- https://git.kernel.org/stable/c/db03727b4bbbbb36e6ef4cb655c670eefb6448e9
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49555.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49555
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
