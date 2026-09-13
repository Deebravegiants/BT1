# [H] wifi: ath6kl: fix OOB read from firmware IE lengths in connect event

## Summary
Severity: High
Advisory: CVE-2026-68352
Ecosystem: Linux
CVSS: 8.3 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68352
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.2.0 <5.10.265, >=5.11.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.148, >=6.7.0 <6.12.101, >=6.13.0 <6.18.42, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: ath6kl: fix OOB read from firmware IE lengths in connect event

The firmware-controlled beacon_ie_len, assoc_req_len, and assoc_resp_len
fields in ath6kl_wmi_connect_event_rx() are not validated against the
buffer length. Their sum (up to 765) can exceed the actual WMI event
data, causing out-of-bounds reads during IE parsing and state corruption
of wmi->is_wmm_enabled.

Add a check that the total IE length fits within the buffer.

## References
- https://git.kernel.org/stable/c/1c690f7c4c5b37108ac8c98b94ce1b3c655a4f5e
- https://git.kernel.org/stable/c/1eeed9efc9a40e0635e910c37fee86543041b4e1
- https://git.kernel.org/stable/c/33b5342d2080657054ddf89ef1199b426a37dae8
- https://git.kernel.org/stable/c/6b47b29730de3232b919d8362749f6814c5f2a33
- https://git.kernel.org/stable/c/7cae33e3e09a080db96e3a8980c2c8d288318320
- https://git.kernel.org/stable/c/94e1bfcefe8264a207c2fda2febb954e70a34b42
- https://git.kernel.org/stable/c/a38d7d6376b295245b53bc98b7ca682c027abaf7
- https://git.kernel.org/stable/c/d70c0a850c21b57a6f46ce363860203389bbeaa6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68352.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68352
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
