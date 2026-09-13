# [H] bnxt_en: Disable EOP for TPA on all chips to prevent data corruption

## Summary
Severity: High
Advisory: CVE-2026-74697
Ecosystem: Linux
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:L)
Published: 2026-08-22
Source: https://osv.dev/vulnerability/CVE-2026-74697
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.4.0 <5.10.265, >=5.11.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.152, >=6.7.0 <6.18.45, >=6.19.0 <7.1.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

bnxt_en: Disable EOP for TPA on all chips to prevent data corruption

EOP (End of frame padding) on the AGG ring may cause overlapping of
zero padding at the end of one segment with the next segment's data.
If Relaxed Ordering (RO) is enabled, the zero padding may overwrite
valid data in the next segment and corrupt the data.  Older chips
(P5 and older) do not automatically disable RO when EOP is enabled.
On some ARM systems, data corruption was reported on 57508 (P5)
chips with RO enabled.

Always disable EOP on all chips on the AGG rings when TPA is enabled
to fix the data corruption.

## References
- https://git.kernel.org/stable/c/410da4428b1f47bf9a84bdc0bcaa089d73ba2048
- https://git.kernel.org/stable/c/68c181af7cd1ca9cbf29acd95911073bfd3c6397
- https://git.kernel.org/stable/c/7aee22a35978b44784612c156e358e375ddf5d16
- https://git.kernel.org/stable/c/aab3b5f4d8ec8598606ee011e219ef824ae25ca0
- https://git.kernel.org/stable/c/b61c4911204a0a2f900e538d64ceb608f6c9614d
- https://git.kernel.org/stable/c/c1962ab4645a914a91ff492735881150ddc8a79e
- https://git.kernel.org/stable/c/c3faf548a00f4c17100cc9204746975fa46a73b9
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74697.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74697
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
