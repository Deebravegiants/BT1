# [H] wifi: nl80211: reject oversized EMA RNR lists

## Summary
Severity: High
Advisory: CVE-2026-53182
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-53182
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.1.176, >=6.2.0 <6.6.143, >=6.4.0 <6.12.94, >=6.7.0 <6.18.36, >=6.13.0 <7.0.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: nl80211: reject oversized EMA RNR lists

nl80211_parse_rnr_elems() stores the parsed element count in a
u8-backed cfg80211_rnr_elems::cnt field and uses that count to size
the flexible array allocation.

Reject nested NL80211_ATTR_EMA_RNR_ELEMS input once the count reaches
255, before incrementing it again. This keeps the parser aligned with
the data structure it fills and matches the existing bound check used
by nl80211_parse_mbssid_elems().

## References
- https://git.kernel.org/stable/c/265c07c09c837621730d35f02975207a1224bf05
- https://git.kernel.org/stable/c/30c3fa80f423613efdda3deca4af52ff7d20e4e2
- https://git.kernel.org/stable/c/4cd92957e8f8cc4ebfe8a5d4203c14c592fde6b1
- https://git.kernel.org/stable/c/688fcac7054abc680c0eef753f2bb772cfaf8cf7
- https://git.kernel.org/stable/c/ecbf3c45add30a0857414e156bdb9c79906f0ff6
- https://git.kernel.org/stable/c/fc0ec2fc02dfe52c5821f36fbccf6a45df43f508
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53182.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53182
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
