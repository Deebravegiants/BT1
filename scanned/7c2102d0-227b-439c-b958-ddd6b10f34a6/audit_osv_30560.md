# [H] wifi: ath9k: add range check for conn_rsp_epid in htc_connect_service()

## Summary
Severity: High
Advisory: CVE-2024-53156
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-12-24
Source: https://osv.dev/vulnerability/CVE-2024-53156
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.35 <4.19.325, >=4.20.0 <5.4.287, >=5.5.0 <5.10.231, >=5.11.0 <5.15.174, >=5.16.0 <6.1.120, >=6.2.0 <6.6.64, >=6.7.0 <6.11.11, >=6.12.0 <6.12.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: ath9k: add range check for conn_rsp_epid in htc_connect_service()

I found the following bug in my fuzzer:

  UBSAN: array-index-out-of-bounds in drivers/net/wireless/ath/ath9k/htc_hst.c:26:51
  index 255 is out of range for type 'htc_endpoint [22]'
  CPU: 0 UID: 0 PID: 8 Comm: kworker/0:0 Not tainted 6.11.0-rc6-dirty #14
  Hardware name: QEMU Standard PC (i440FX + PIIX, 1996), BIOS 1.15.0-1 04/01/2014
  Workqueue: events request_firmware_work_func
  Call Trace:
   <TASK>
   dump_stack_lvl+0x180/0x1b0
   __ubsan_handle_out_of_bounds+0xd4/0x130
   htc_issue_send.constprop.0+0x20c/0x230
   ? _raw_spin_unlock_irqrestore+0x3c/0x70
   ath9k_wmi_cmd+0x41d/0x610
   ? mark_held_locks+0x9f/0xe0
   ...

Since this bug has been confirmed to be caused by insufficient verification
of conn_rsp_epid, I think it would be appropriate to add a range check for
conn_rsp_epid to htc_connect_service() to prevent the bug from occurring.

## References
- https://git.kernel.org/stable/c/3fe99b9690b99606d3743c9961ebee865cfa1ab8
- https://git.kernel.org/stable/c/5f177fb9d01355ac183e65ad8909ea8ef734e0cf
- https://git.kernel.org/stable/c/70eae50d2156cb6e078d0d78809b49bf2f4c7540
- https://git.kernel.org/stable/c/8619593634cbdf5abf43f5714df49b04e4ef09ab
- https://git.kernel.org/stable/c/8965db7fe2e913ee0802b05fc94c6d6aa74e0596
- https://git.kernel.org/stable/c/b6551479daf2bfa80bfd5d9016b02a810e508bfb
- https://git.kernel.org/stable/c/bc981179ab5d1a2715f35e3db4e4bb822bacc849
- https://git.kernel.org/stable/c/c941af142200d975dd3be632aeb490f4cb91dae4
- https://git.kernel.org/stable/c/cb480ae80fd4d0f1ac9e107ce799183beee5124b
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/53xxx/CVE-2024-53156.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-53156
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
