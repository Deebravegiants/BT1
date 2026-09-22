# [H] netfilter: ebtables: fix OOB read in compat_mtw_from_user

## Summary
Severity: High
Advisory: CVE-2026-52927
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-52927
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.34 <5.10.259, >=5.11.0 <5.15.210, >=5.16.0 <6.1.176, >=6.2.0 <6.6.143, >=6.7.0 <6.12.93, >=6.13.0 <6.18.35, >=6.19.0 <7.0.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: ebtables: fix OOB read in compat_mtw_from_user

Luxiao Xu says:

 The function compat_mtw_from_user() converts ebtables extensions from
 32-bit user structures to kernel native structures. However, it lacks
 proper validation of the user-supplied match_size/target_size.

 When certain extensions are processed, the kernel-side translation
 logic may perform memory accesses based on the extension's expected
 size. If the user provides a size smaller than what the extension
 requires, it results in an out-of-bounds read as reported by KASAN.

 This fix introduces a check to ensure match_size is at least as large
 as the extension's required compatsize. This covers matches, watchers,
 and targets, while maintaining compatibility with standard targets.

AFAIU this is relevant for matches that need to go though
match->compat_from_user() call.  Those that use plain memcpy with the
user-provided size are ok because the caller checks that size vs the
start of the next rule entry offset (which itself is checked vs. total
size copied from userspace).

The ->compat_from_user() callbacks assume they can read compatsize bytes,
so they need this extra check.

Based on an earlier patch from Luxiao Xu.

## References
- https://git.kernel.org/stable/c/21af4c030567d2e6c89bb927bc18b51fba52a400
- https://git.kernel.org/stable/c/7ad0e463fc7eafae2141cc38054264636f8b3e94
- https://git.kernel.org/stable/c/a27cb7325a6c69970041c7f8541fafed5a1ea3ec
- https://git.kernel.org/stable/c/bf8e8eac7ede51dc318e06acef5a896dcbba7595
- https://git.kernel.org/stable/c/d7a8fb6f10d55a1c37b0bf8c20cca24dffd76e00
- https://git.kernel.org/stable/c/dad9ebf8107955bb54bd3f9cf22591b6ff37bac1
- https://git.kernel.org/stable/c/f438d1786d657d57790c5d138d6db3fc9fdac392
- https://git.kernel.org/stable/c/fcc4c043d137e7f1de4673dba1f3116e45377c67
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/52xxx/CVE-2026-52927.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-52927
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
