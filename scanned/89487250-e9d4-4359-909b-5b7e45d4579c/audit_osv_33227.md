# [H] wifi: mt76: mt7996: add missing check for rx wcid entries

## Summary
Severity: High
Advisory: CVE-2025-39919
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-01
Source: https://osv.dev/vulnerability/CVE-2025-39919
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.15.0 <6.16.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: mt76: mt7996: add missing check for rx wcid entries

Non-station wcid entries must not be passed to the rx functions.
In case of the global wcid entry, it could even lead to corruption in the wcid
array due to pointer being casted to struct mt7996_sta_link using container_of.

## References
- https://git.kernel.org/stable/c/4a522b01e368eec58d182ecc47d24f49a39e440d
- https://git.kernel.org/stable/c/69dcc19048fcdc3fb166fd25b805470ee8fc0eb1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39919.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39919
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
