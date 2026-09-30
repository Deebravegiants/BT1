# [H] wifi: cfg80211: validate EHT MLE before MLD ID read

## Summary
Severity: High
Advisory: CVE-2026-68472
Ecosystem: Linux
CVSS: 8.1 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-68472
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.14.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: cfg80211: validate EHT MLE before MLD ID read

cfg80211_gen_new_ie() copies ML probe response elements from
the parent frame when the parent EHT multi-link element has an
MLD ID matching the nontransmitted BSSID index.

The code only checked that the extension element had more than
one byte before calling ieee80211_mle_get_mld_id(). That helper
assumes a BASIC MLE with enough common info and documents that
callers must first use ieee80211_mle_type_ok().

Attack chain:
malicious AP sends a short EHT MLE in an MBSSID beacon.
cfg80211_inform_bss_frame_data() stores the copied IE buffer.
cfg80211_parse_mbssid_data() builds the nontransmitted BSS IE.
cfg80211_gen_new_ie() sees the EHT MLE in the parent frame.
ieee80211_mle_get_mld_id() then reads past the IE boundary.

Validate the MLE type and size before reading the MLD ID. This
matches the contract required by the MLE helper and rejects the
short element before any internal MLE fields are accessed.

## References
- https://git.kernel.org/stable/c/3b0505e43da8fb5b2a7994c3c3604e5a74692154
- https://git.kernel.org/stable/c/584657c5fc58d7a840623a2fa06331c9661dd0f1
- https://git.kernel.org/stable/c/74e27cd1d98b546fdb276008a83708d062339661
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68472.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68472
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
