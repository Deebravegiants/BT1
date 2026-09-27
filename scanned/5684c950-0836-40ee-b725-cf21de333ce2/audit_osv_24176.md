# [M] mm: /proc/pid/smaps_rollup: fix no vma's null-deref

## Summary
Severity: Medium
Advisory: CVE-2022-50380
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-18
Source: https://osv.dev/vulnerability/CVE-2022-50380
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.19.0 <4.19.264, >=4.20.0 <5.4.221, >=5.5.0 <5.10.152, >=5.11.0 <5.15.76, >=5.16.0 <6.0.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

mm: /proc/pid/smaps_rollup: fix no vma's null-deref

Commit 258f669e7e88 ("mm: /proc/pid/smaps_rollup: convert to single value
seq_file") introduced a null-deref if there are no vma's in the task in
show_smaps_rollup.

## References
- https://git.kernel.org/stable/c/33fc9e26b7cb39f0d4219c875a2451802249c225
- https://git.kernel.org/stable/c/6bb8769326c46db3058780c0640dcc49d8187b24
- https://git.kernel.org/stable/c/97898139ca9b81ba9322a585e07490983c53b55a
- https://git.kernel.org/stable/c/a50ed2d28727ff605d95fb9a53be8ff94e8eaaf4
- https://git.kernel.org/stable/c/c4c84f06285e48f80e9843d0775ad92714ffc35a
- https://git.kernel.org/stable/c/dbe863bce7679c7f5ec0e993d834fe16c5e687b5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50380.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50380
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
