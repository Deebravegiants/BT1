# [H] CVE-2021-47251

## Summary
Severity: High
Advisory: CVE-2021-47251
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2021-47251
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

mac80211: fix skb length check in ieee80211_scan_rx()

Replace hard-coded compile-time constants for header length check
with dynamic determination based on the frame type. Otherwise, we
hit a validation WARN_ON in cfg80211 later.

[style fixes, reword commit message]

## References
- https://git.kernel.org/stable/c/d1b949c70206178b12027f66edc088d40375b5cb
- https://git.kernel.org/stable/c/e298aa358f0ca658406d524b6639fe389cb6e11e
- https://git.kernel.org/stable/c/5a1cd67a801cf5ef989c4783e07b86a25b143126
