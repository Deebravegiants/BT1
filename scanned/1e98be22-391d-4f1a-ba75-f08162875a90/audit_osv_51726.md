# [M] CVE-2021-38206

## Summary
Severity: Medium
Advisory: CVE-2021-38206
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-08-08
Source: https://osv.dev/vulnerability/CVE-2021-38206
Type: osv

## Details
The mac80211 subsystem in the Linux kernel before 5.12.13, when a device supporting only 5 GHz is used, allows attackers to cause a denial of service (NULL pointer dereference in the radiotap parser) by injecting a frame with 802.11a rates.

## References
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.12.13
- https://github.com/torvalds/linux/commit/bddc0c411a45d3718ac535a070f349be8eca8d48
