# [H] ASoC: amd: acp-sdw-sof: Bound DAI link iteration

## Summary
Severity: High
Advisory: CVE-2026-74332
Ecosystem: Linux
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74332
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.12.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

ASoC: amd: acp-sdw-sof: Bound DAI link iteration

create_sdw_dailinks() walks sof_dais until it finds an entry with
initialised cleared, but sof_dais is allocated with exactly num_ends
entries. If all entries are initialised, the loop reads past the end of
the array.

Pass the allocated entry count to create_sdw_dailinks() and stop before
reading past the array.

## References
- https://git.kernel.org/stable/c/0a5ff4000dd7a390139dd7823fef1de4963e490a
- https://git.kernel.org/stable/c/4d992e63f52d58f52b724606c60ae7b37a1c582f
- https://git.kernel.org/stable/c/86a64c049873fe4d4a6a378e27a333ab5631c4b2
- https://git.kernel.org/stable/c/9e82497138abea7d5c6e65015663d907fbcbf6b4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74332.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74332
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
