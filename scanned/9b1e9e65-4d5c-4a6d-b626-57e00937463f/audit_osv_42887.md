# [H] dm era: fix out-of-bounds memory access for non-zero start sector

## Summary
Severity: High
Advisory: CVE-2026-72107
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72107
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.15.0 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

dm era: fix out-of-bounds memory access for non-zero start sector

dm-era tracks writes in target-relative blocks, but era_map() calculates
the writeset block before applying the target offset.  Tables with a
non-zero start sector can therefore pass an absolute mapped-device block
to metadata_current_marked().

If the absolute block is beyond the current writeset size,
writeset_marked() tests past the end of the in-core bitset.  KASAN reports
this as a vmalloc-out-of-bounds access.

Apply the target offset before calculating the era block so writeset
lookups use the target-relative block number.

## References
- https://git.kernel.org/stable/c/1fcb5e29dd7a5b85adb9d8b539911741d878e829
- https://git.kernel.org/stable/c/7e1822f83c5a1ee7b4a19e98edde8770a10b4c71
- https://git.kernel.org/stable/c/9946a7176bd8c25ddd6e5f1799c54e572ee6bf0f
- https://git.kernel.org/stable/c/a868196f03c2b19418ae3d2b69e195d668a271e5
- https://git.kernel.org/stable/c/bafe3e720cdac38cd7ea4eb7852a8f2dbe1bbfe6
- https://git.kernel.org/stable/c/db5f9b4601f0012038e5a2628aedec2f47933380
- https://git.kernel.org/stable/c/e3ffa8e492e5cdee62d916ee3e9244ccce2b73c5
- https://git.kernel.org/stable/c/fe94a0b14010a3c267ff9a2508afb4f27ff1c5bf
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72107.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72107
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
