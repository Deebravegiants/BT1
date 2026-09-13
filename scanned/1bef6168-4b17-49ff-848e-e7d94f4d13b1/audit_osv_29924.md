# [H] wifi: mt76: mt7996: use hweight16 to get correct tx antenna

## Summary
Severity: High
Advisory: CVE-2024-47714
Ecosystem: Linux
CVSS: 7.6 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:H)
Published: 2024-10-21
Source: https://osv.dev/vulnerability/CVE-2024-47714
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.2.0 <6.6.54, >=6.7.0 <6.10.13, >=6.11.0 <6.11.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: mt76: mt7996: use hweight16 to get correct tx antenna

The chainmask is u16 so using hweight8 cannot get correct tx_ant.
Without this patch, the tx_ant of band 2 would be -1 and lead to the
following issue:
BUG: KASAN: stack-out-of-bounds in mt7996_mcu_add_sta+0x12e0/0x16e0 [mt7996e]

## References
- https://git.kernel.org/stable/c/33954930870c18ec549e4bca0eeff43e252cb740
- https://git.kernel.org/stable/c/50d87e3b70980abc090676b6b4703fcbd96221f9
- https://git.kernel.org/stable/c/8f51fc8a9e2fd96363d8ec3f4ee4b78dd64754e3
- https://git.kernel.org/stable/c/f98c3de92bb05dac4a4969df8a4595ed380b4604
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/47xxx/CVE-2024-47714.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-47714
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
