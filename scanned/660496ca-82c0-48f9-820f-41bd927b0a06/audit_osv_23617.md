# [M] mt76: mt7921s: fix a possible memory leak in mt7921_load_patch

## Summary
Severity: Medium
Advisory: CVE-2022-49225
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49225
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.17.0 <5.17.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

mt76: mt7921s: fix a possible memory leak in mt7921_load_patch

Always release fw data at the end of mt7921_load_patch routine.

## References
- https://git.kernel.org/stable/c/11005b18f453aa192d035d410c11d07edcba5a45
- https://git.kernel.org/stable/c/b301043384c5c2447357952be9a536c2026d8ad0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49225.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49225
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
