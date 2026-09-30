# [H] wifi: mac80211: bounds-check link_id in ieee80211_ml_epcs

## Summary
Severity: High
Advisory: CVE-2026-64030
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-64030
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.15.0 <6.18.34, >=6.19.0 <7.0.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: mac80211: bounds-check link_id in ieee80211_ml_epcs

IEEE80211_MLE_STA_EPCS_CONTROL_LINK_ID is 0x000f, so link_id extracted
from a PRIO_ACCESS ML element PER_STA_PROFILE subelement can be 0..15.
sdata->link[] has IEEE80211_MLD_MAX_NUM_LINKS (15) entries (indices 0..14),
making index 15 out-of-bounds.

A connected WiFi 7 AP can trigger this by sending an EPCS Enable Response
action frame with a PER_STA_PROFILE subelement where link_id = 15.  The
unsolicited-notification path (dialog_token = 0) is reachable any time
EPCS is already enabled, without any prior client request.

sdata->link[15] reads into the first word of sdata->activate_links_work
(a wiphy_work whose embedded list_head is non-NULL after INIT_LIST_HEAD),
so the NULL check on the result does not catch the invalid access.  The
garbage pointer is then passed to ieee80211_sta_wmm_params(), which
dereferences link->sdata and crashes the kernel.

The same class of bug was fixed for ieee80211_ml_reconfiguration() by
commit 162d331d833d ("wifi: mac80211: bounds-check link_id in
ieee80211_ml_reconfiguration").

## References
- https://git.kernel.org/stable/c/2d8379834800c30602f24c71ab7c40f5fe84d200
- https://git.kernel.org/stable/c/863f1f02a3bd70dbd857b8ac4070292fde8cb4e2
- https://git.kernel.org/stable/c/f718506edd2d9c6a308ded9d13c632bf7b7d5a2c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64030.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64030
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
