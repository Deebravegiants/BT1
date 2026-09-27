# [H] wifi: mac80211_hwsim: drop short frames

## Summary
Severity: High
Advisory: CVE-2023-53321
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2025-09-16
Source: https://osv.dev/vulnerability/CVE-2023-53321
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.4.0 <5.4.257, >=5.5.0 <5.10.197, >=5.11.0 <5.15.133, >=5.16.0 <6.1.55, >=6.2.0 <6.5.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: mac80211_hwsim: drop short frames

While technically some control frames like ACK are shorter and
end after Address 1, such frames shouldn't be forwarded through
wmediumd or similar userspace, so require the full 3-address
header to avoid accessing invalid memory if shorter frames are
passed in.

## References
- https://git.kernel.org/stable/c/3beb97bed860d95b14ad23578ce8ddaea62023db
- https://git.kernel.org/stable/c/672205c6f2d11978fcd7f0f336bb2c708e28874b
- https://git.kernel.org/stable/c/89a41ed7f21476301659ebd25ccb48a60791c1a7
- https://git.kernel.org/stable/c/b9a175e3b250b0dc6e152988040aa5014e98e61e
- https://git.kernel.org/stable/c/c64ee9dd335832d5e2ab0a8fc83a34ad4c729799
- https://git.kernel.org/stable/c/fba360a047d5eeeb9d4b7c3a9b1c8308980ce9a6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53321.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53321
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
