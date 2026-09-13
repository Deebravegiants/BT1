# [H] x86/lam: Disable ADDRESS_MASKING in most cases

## Summary
Severity: High
Advisory: CVE-2024-50112
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-11-05
Source: https://osv.dev/vulnerability/CVE-2024-50112
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.4.0 <6.6.59, >=6.7.0 <6.11.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

x86/lam: Disable ADDRESS_MASKING in most cases

Linear Address Masking (LAM) has a weakness related to transient
execution as described in the SLAM paper[1]. Unless Linear Address
Space Separation (LASS) is enabled this weakness may be exploitable.

Until kernel adds support for LASS[2], only allow LAM for COMPILE_TEST,
or when speculation mitigations have been disabled at compile time,
otherwise keep LAM disabled.

There are no processors in market that support LAM yet, so currently
nobody is affected by this issue.

[1] SLAM: https://download.vusec.net/papers/slam_sp24.pdf
[2] LASS: https://lore.kernel.org/lkml/20230609183632.48706-1-alexander.shishkin@linux.intel.com/

[ dhansen: update SPECULATION_MITIGATIONS -> CPU_MITIGATIONS ]

## References
- https://git.kernel.org/stable/c/3267cb6d3a174ff83d6287dcd5b0047bbd912452
- https://git.kernel.org/stable/c/60a5ba560f296ad8da153f6ad3f70030bfa3958f
- https://git.kernel.org/stable/c/690599066488d16db96ac0d6340f9372fc56f337
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50112.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50112
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
