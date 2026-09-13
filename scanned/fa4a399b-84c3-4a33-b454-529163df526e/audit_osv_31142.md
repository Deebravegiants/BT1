# [M] wifi: cfg80211: tests: Fix potential NULL dereference in test_cfg80211_parse_colocated_ap()

## Summary
Severity: Medium
Advisory: CVE-2024-58064
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-03-06
Source: https://osv.dev/vulnerability/CVE-2024-58064
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.9.0 <6.12.13, >=6.13.0 <6.13.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: cfg80211: tests: Fix potential NULL dereference in test_cfg80211_parse_colocated_ap()

kunit_kzalloc() may return NULL, dereferencing it without NULL check may
lead to NULL dereference.
Add a NULL check for ies.

## References
- https://git.kernel.org/stable/c/0d17d81143f5aa56ee87e60bb1000a2372a0ada8
- https://git.kernel.org/stable/c/13c4f7714c6a1ecf748a2f22099447c14fe6ed8c
- https://git.kernel.org/stable/c/886271409603956edd09df229dde7442c410a872
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/58xxx/CVE-2024-58064.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-58064
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
