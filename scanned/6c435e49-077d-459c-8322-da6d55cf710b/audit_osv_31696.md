# [M] rds: sysctl: rds_tcp_{rcv,snd}buf: avoid using current->nsproxy

## Summary
Severity: Medium
Advisory: CVE-2025-21635
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-01-19
Source: https://osv.dev/vulnerability/CVE-2025-21635
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.6.0 <6.12.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

rds: sysctl: rds_tcp_{rcv,snd}buf: avoid using current->nsproxy

As mentioned in a previous commit of this series, using the 'net'
structure via 'current' is not recommended for different reasons:

- Inconsistency: getting info from the reader's/writer's netns vs only
  from the opener's netns.

- current->nsproxy can be NULL in some cases, resulting in an 'Oops'
  (null-ptr-deref), e.g. when the current task is exiting, as spotted by
  syzbot [1] using acct(2).

The per-netns structure can be obtained from the table->data using
container_of(), then the 'net' one can be retrieved from the listen
socket (if available).

## References
- https://git.kernel.org/stable/c/7f5611cbc4871c7fb1ad36c2e5a9edad63dca95c
- https://git.kernel.org/stable/c/de8d6de0ee27be4b2b1e5b06f04aeacbabbba492
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21635.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21635
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
