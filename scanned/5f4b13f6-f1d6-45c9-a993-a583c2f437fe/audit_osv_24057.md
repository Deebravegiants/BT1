# [H] wifi: mac80211: Fix UAF in ieee80211_scan_rx()

## Summary
Severity: High
Advisory: CVE-2022-49934
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-06-18
Source: https://osv.dev/vulnerability/CVE-2022-49934
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.19.0 <4.9.330, >=4.10.0 <4.14.295, >=4.15.0 <4.19.260, >=4.20.0 <5.4.215, >=5.5.0 <5.10.142, >=5.11.0 <5.15.66, >=5.16.0 <5.19.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: mac80211: Fix UAF in ieee80211_scan_rx()

ieee80211_scan_rx() tries to access scan_req->flags after a
null check, but a UAF is observed when the scan is completed
and __ieee80211_scan_completed() executes, which then calls
cfg80211_scan_done() leading to the freeing of scan_req.

Since scan_req is rcu_dereference()'d, prevent the racing in
__ieee80211_scan_completed() by ensuring that from mac80211's
POV it is no longer accessed from an RCU read critical section
before we call cfg80211_scan_done().

## References
- https://git.kernel.org/stable/c/4abc8c07a065ecf771827bde3c63fbbe4aa0c08b
- https://git.kernel.org/stable/c/5d20c6f932f2758078d0454729129c894fe353e7
- https://git.kernel.org/stable/c/60deb9f10eec5c6a20252ed36238b55d8b614a2c
- https://git.kernel.org/stable/c/6eb181a64fdabf10be9e54de728876667da20255
- https://git.kernel.org/stable/c/78a07732fbb0934d14827d8f09b9aa6a49ee1aa9
- https://git.kernel.org/stable/c/9ad48cbf8b07f10c1e4a7a262b32a9179ae9dd2d
- https://git.kernel.org/stable/c/c0445feb80a4d0854898118fa01073701f8d356b
- https://git.kernel.org/stable/c/e0ff39448cea654843744c72c6780293c5082cb1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49934.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49934
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
