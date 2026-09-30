# [H] wifi: mac80211: validate individual TWT params before driver setup

## Summary
Severity: High
Advisory: CVE-2026-80722
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/CVE-2026-80722
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.151, >=6.7.0 <6.12.103, >=6.13.0 <6.18.44, >=6.19.0 <7.1.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: mac80211: validate individual TWT params before driver setup

ieee80211_process_rx_twt_action() only partially validates a received
S1G TWT setup frame before queueing it.

An individual agreement can therefore reach ieee80211_s1g_rx_twt_setup()
with twt->length too short for the full struct ieee80211_twt_params.

The individual path passes twt to drv_add_twt_setup(). Both the tracepoint
and the driver callback consume the complete parameters block, not merely
req_type. Do not pass a short individual agreement to the driver.
Broadcast agreements remain unchanged because they are rejected locally
after accessing only req_type.

[edit commit message to not overclaim lack of validation nor
 understate driver impact]

## References
- https://git.kernel.org/stable/c/0502d5077e419427d80f4d46ba95d0067f5fb916
- https://git.kernel.org/stable/c/09d60d1f72e6598241490eb6c4e97245af895c09
- https://git.kernel.org/stable/c/47fb04c3826e1f90271d405523043d6708b9072a
- https://git.kernel.org/stable/c/92fcd0f30dc8e51f252589b082d46851d295cc1a
- https://git.kernel.org/stable/c/ade9e2f0f7f4d3089600ac2af8ef0b91746f923b
- https://git.kernel.org/stable/c/b558e07708d886acfcf4b0391ed7a8546e81d326
- https://git.kernel.org/stable/c/ff558072d199c1d641d1561da622e67f780514de
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80722.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80722
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
