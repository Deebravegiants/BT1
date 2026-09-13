# [H] jbd2: fix integer underflow in jbd2_journal_initialize_fast_commit()

## Summary
Severity: High
Advisory: CVE-2026-72225
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72225
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.10.0 <5.10.266, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

jbd2: fix integer underflow in jbd2_journal_initialize_fast_commit()

jbd2_journal_initialize_fast_commit() validates journal capacity by
checking (journal->j_last - num_fc_blks < JBD2_MIN_JOURNAL_BLOCKS).
Both j_last and num_fc_blks are unsigned, so when num_fc_blks exceeds
j_last the subtraction wraps to a large value, bypassing the bounds
check.

The resulting underflow corrupts j_last, j_fc_first, and j_free,
leading to journal abort.

Fix by checking num_fc_blks against j_last before the subtraction,
returning -EFSCORRUPTED.

## References
- https://git.kernel.org/stable/c/289a2ca0c9b7eae74f93fc213b0b971669b8683d
- https://git.kernel.org/stable/c/4450dcaadf7d4aae8b6e4223b5d6ee4eb77097a9
- https://git.kernel.org/stable/c/4b48dcb88bb9117e3d3f051175a9a8b7cff7f8b6
- https://git.kernel.org/stable/c/78955fdce8ff654e6d33a2fa90882a1e7eb26330
- https://git.kernel.org/stable/c/a58fc10adf503969fec2007b5afe8987258046c4
- https://git.kernel.org/stable/c/aa90f00932bf572d6ef284c977c2a60b39c13bd6
- https://git.kernel.org/stable/c/e144ad0250f77e23e28949587b8b57e40dc3b512
- https://git.kernel.org/stable/c/fb9b49618ed7296ebfad62a3835da8945f727001
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72225.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72225
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
