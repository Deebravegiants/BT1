# [H] md/raid1,raid10: fix error-path detection with md_cloned_bio()

## Summary
Severity: High
Advisory: CVE-2026-74374
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74374
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.12.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

md/raid1,raid10: fix error-path detection with md_cloned_bio()

Detect the error path using md_cloned_bio() instead of relying
on r1_bio in raid1 or r10_bio->read_slot in raid10, which may be
NULL or -1 after splitting and resubmitting a failed bio.

As a result, the error path may not be recognized and memory
allocations can incorrectly use GFP_NOIO instead of
(GFP_NOIO | __GFP_HIGH), which can lead to a deadlock under
memory pressure.

## References
- https://git.kernel.org/stable/c/20fb582c92fd64e5c8bd83c6176264b2794603b7
- https://git.kernel.org/stable/c/811545e0926d02a6a0b1a1258bb5544777c164d4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74374.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74374
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
