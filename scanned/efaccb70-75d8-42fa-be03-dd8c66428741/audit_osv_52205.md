# [H] CVE-2021-47194

## Summary
Severity: High
Advisory: CVE-2021-47194
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-04-10
Source: https://osv.dev/vulnerability/CVE-2021-47194
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

cfg80211: call cfg80211_stop_ap when switch from P2P_GO type

If the userspace tools switch from NL80211_IFTYPE_P2P_GO to
NL80211_IFTYPE_ADHOC via send_msg(NL80211_CMD_SET_INTERFACE), it
does not call the cleanup cfg80211_stop_ap(), this leads to the
initialization of in-use data. For example, this path re-init the
sdata->assigned_chanctx_list while it is still an element of
assigned_vifs list, and makes that linked list corrupt.

## References
- https://git.kernel.org/stable/c/563fbefed46ae4c1f70cffb8eb54c02df480b2c2
- https://git.kernel.org/stable/c/5a9b671c8d74a3e1b999e7a0c7f366079bcc93dd
- https://git.kernel.org/stable/c/7b97b5776daa0b39dbdadfea176f9cc0646d4a66
- https://git.kernel.org/stable/c/8f06bb8c216bcd172394f61e557727e691b4cb24
- https://git.kernel.org/stable/c/b8a045e2a9b234cfbc06cf36923886164358ddec
- https://git.kernel.org/stable/c/0738cdb636c21ab552eaecf905efa4a6070e3ebc
- https://git.kernel.org/stable/c/4e458abbb4a523f1413bfe15c079cf4e24c15b21
- https://git.kernel.org/stable/c/52affc201fc22a1ab9a59ef0ed641a9adfcb8d13
