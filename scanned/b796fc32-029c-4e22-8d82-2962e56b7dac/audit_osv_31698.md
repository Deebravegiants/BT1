# [M] mptcp: sysctl: blackhole timeout: avoid using current->nsproxy

## Summary
Severity: Medium
Advisory: CVE-2025-21641
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-01-19
Source: https://osv.dev/vulnerability/CVE-2025-21641
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.12.0 <6.12.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

mptcp: sysctl: blackhole timeout: avoid using current->nsproxy

As mentioned in the previous commit, using the 'net' structure via
'current' is not recommended for different reasons:

- Inconsistency: getting info from the reader's/writer's netns vs only
  from the opener's netns.

- current->nsproxy can be NULL in some cases, resulting in an 'Oops'
  (null-ptr-deref), e.g. when the current task is exiting, as spotted by
  syzbot [1] using acct(2).

The 'pernet' structure can be obtained from the table->data using
container_of().

## References
- https://git.kernel.org/stable/c/4c74fbdc5ab95b13945be01e6065940b68222db7
- https://git.kernel.org/stable/c/92cf7a51bdae24a32c592adcdd59a773ae149289
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21641.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21641
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
