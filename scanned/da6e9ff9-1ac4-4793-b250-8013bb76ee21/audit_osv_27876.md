# [H] wifi: mac80211: fix RCU use in TDLS fast-xmit

## Summary
Severity: High
Advisory: CVE-2024-26666
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:A/AC:H/PR:N/UI:N/S:U/C:H/I:L/A:H)
Published: 2024-04-02
Source: https://osv.dev/vulnerability/CVE-2024-26666
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.5.0 <6.6.17, >=6.7.0 <6.7.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: mac80211: fix RCU use in TDLS fast-xmit

This looks up the link under RCU protection, but isn't
guaranteed to actually have protection. Fix that.

## References
- https://git.kernel.org/stable/c/9480adfe4e0f0319b9da04b44e4eebd5ad07e0cd
- https://git.kernel.org/stable/c/c255c3b653c6e8b52ac658c305e2fece2825f7ad
- https://git.kernel.org/stable/c/fc3432ae8232ff4025e7c55012dd88db0e3d18eb
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26666.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26666
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
