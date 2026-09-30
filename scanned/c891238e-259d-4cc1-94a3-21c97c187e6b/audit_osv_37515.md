# [H] wifi: iwlwifi: mvm: fix potential out-of-bounds read in iwl_mvm_nd_match_info_handler()

## Summary
Severity: High
Advisory: CVE-2026-31779
Ecosystem: Linux
CVSS: 8.1 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-05-01
Source: https://osv.dev/vulnerability/CVE-2026-31779
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.1.0 <6.1.168, >=6.2.0 <6.6.134, >=6.7.0 <6.12.81, >=6.13.0 <6.18.22, >=6.19.0 <6.19.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: iwlwifi: mvm: fix potential out-of-bounds read in iwl_mvm_nd_match_info_handler()

The memcpy function assumes the dynamic array notif->matches is at least
as large as the number of bytes to copy. Otherwise, results->matches may
contain unwanted data. To guarantee safety, extend the validation in one
of the checks to ensure sufficient packet length.

Found by Linux Verification Center (linuxtesting.org) with SVACE.

## References
- https://git.kernel.org/stable/c/744fabc338e87b95c4d1ff7c95bc8c0f834c6d99
- https://git.kernel.org/stable/c/ca0e9491b98ca4c5b44204b0b3dd8062a3b5fba2
- https://git.kernel.org/stable/c/dd90880eb5ec5442b37eb2b95688f4a63f4883e3
- https://git.kernel.org/stable/c/e67d8c626ace80b0fa2b48c8ec0a46b508c93442
- https://git.kernel.org/stable/c/f6abac936a0dfd31d6c3e49205ec0ee75a8f887f
- https://git.kernel.org/stable/c/ffbed27ba15ef80d1c622eeedbfef03e501ae134
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31779.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31779
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
