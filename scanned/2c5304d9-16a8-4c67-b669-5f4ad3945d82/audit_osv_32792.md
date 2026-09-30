# [H] wifi: cfg80211: fix out-of-bounds access during multi-link element defragmentation

## Summary
Severity: High
Advisory: CVE-2025-37973
Ecosystem: Linux
CVSS: 8.1 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2025-05-20
Source: https://osv.dev/vulnerability/CVE-2025-37973
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.5.0 <6.6.91, >=6.7.0 <6.12.29, >=6.13.0 <6.14.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: cfg80211: fix out-of-bounds access during multi-link element defragmentation

Currently during the multi-link element defragmentation process, the
multi-link element length added to the total IEs length when calculating
the length of remaining IEs after the multi-link element in
cfg80211_defrag_mle(). This could lead to out-of-bounds access if the
multi-link element or its corresponding fragment elements are the last
elements in the IEs buffer.

To address this issue, correctly calculate the remaining IEs length by
deducting the multi-link element end offset from total IEs end offset.

## References
- https://git.kernel.org/stable/c/023c1f2f0609218103cbcb48e0104b144d4a16dc
- https://git.kernel.org/stable/c/73dde269a1a43e6b1aa92eba13ad2df58bfdd38e
- https://git.kernel.org/stable/c/9423f6da825172b8dc60d4688ed3d147291c3be9
- https://git.kernel.org/stable/c/e1c6d0c6199bd5f4cfc7a66ae7032b6e805f904d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/37xxx/CVE-2025-37973.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-37973
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
