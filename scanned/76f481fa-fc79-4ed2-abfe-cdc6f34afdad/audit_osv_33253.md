# [H] wifi: mac80211: increase scan_ies_len for S1G

## Summary
Severity: High
Advisory: CVE-2025-39957
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2025-10-09
Source: https://osv.dev/vulnerability/CVE-2025-39957
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.4.0 <6.6.108, >=6.7.0 <6.12.49, >=6.13.0 <6.16.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: mac80211: increase scan_ies_len for S1G

Currently the S1G capability element is not taken into account
for the scan_ies_len, which leads to a buffer length validation
failure in ieee80211_prep_hw_scan() and subsequent WARN in
__ieee80211_start_scan(). This prevents hw scanning from functioning.
To fix ensure we accommodate for the S1G capability length.

## References
- https://git.kernel.org/stable/c/0dbad5f5549e54ac269cc04ce89f212892a98cab
- https://git.kernel.org/stable/c/32adb020b0c32939da1322dcc87fc0ae2bc935d1
- https://git.kernel.org/stable/c/7e2f3213e85eba00acb4cfe6d71647892d63c3a1
- https://git.kernel.org/stable/c/93e063f15e17acb8cd6ac90c8f0802c2624e1a74
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39957.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39957
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
