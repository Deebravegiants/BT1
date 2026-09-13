# [H] wifi: mt76: mt7996: Fix possible OOB access in mt7996_tx()

## Summary
Severity: High
Advisory: CVE-2025-38599
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-08-19
Source: https://osv.dev/vulnerability/CVE-2025-38599
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.15.0 <6.15.10, >=6.16.0 <6.16.1

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: mt76: mt7996: Fix possible OOB access in mt7996_tx()

Fis possible Out-Of-Boundary access in mt7996_tx routine if link_id is
set to IEEE80211_LINK_UNSPECIFIED

## References
- https://git.kernel.org/stable/c/64cbf0d7ce9afe20666da90ec6ecaec6ba5ac64b
- https://git.kernel.org/stable/c/f43e7d8ae4b6a73213032545552bab26f76f113a
- https://git.kernel.org/stable/c/f82eabd0ff8067d1ee95515f4174c9a9569d54cb
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38599.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38599
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
