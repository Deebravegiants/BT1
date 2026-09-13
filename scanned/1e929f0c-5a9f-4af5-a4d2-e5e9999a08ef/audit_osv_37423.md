# [H] futex: Require sys_futex_requeue() to have identical flags

## Summary
Severity: High
Advisory: CVE-2026-31554
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-24
Source: https://osv.dev/vulnerability/CVE-2026-31554
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.7.0 <6.12.80, >=6.13.0 <6.18.21, >=6.19.0 <6.19.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

futex: Require sys_futex_requeue() to have identical flags

Nicholas reported that his LLM found it was possible to create a UaF
when sys_futex_requeue() is used with different flags. The initial
motivation for allowing different flags was the variable sized futex,
but since that hasn't been merged (yet), simply mandate the flags are
identical, as is the case for the old style sys_futex() requeue
operations.

## References
- https://git.kernel.org/stable/c/027145ace09fad4c7cbcd6c61fe9b429c63eb0e5
- https://git.kernel.org/stable/c/18b7d09c2b794c71d4252f3ea2cf84ad12b73d6a
- https://git.kernel.org/stable/c/19f94b39058681dec64a10ebeb6f23fe7fc3f77a
- https://git.kernel.org/stable/c/e2f78c7ec1655fedd945366151ba54fcb9580508
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31554.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31554
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
