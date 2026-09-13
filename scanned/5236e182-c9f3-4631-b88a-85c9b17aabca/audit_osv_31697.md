# [M] sctp: sysctl: plpmtud_probe_interval: avoid using current->nsproxy

## Summary
Severity: Medium
Advisory: CVE-2025-21636
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-01-19
Source: https://osv.dev/vulnerability/CVE-2025-21636
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.14.0 <5.15.177, >=5.16.0 <6.1.125, >=6.2.0 <6.6.72, >=6.7.0 <6.12.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

sctp: sysctl: plpmtud_probe_interval: avoid using current->nsproxy

As mentioned in a previous commit of this series, using the 'net'
structure via 'current' is not recommended for different reasons:

- Inconsistency: getting info from the reader's/writer's netns vs only
  from the opener's netns.

- current->nsproxy can be NULL in some cases, resulting in an 'Oops'
  (null-ptr-deref), e.g. when the current task is exiting, as spotted by
  syzbot [1] using acct(2).

The 'net' structure can be obtained from the table->data using
container_of().

Note that table->data could also be used directly, as this is the only
member needed from the 'net' structure, but that would increase the size
of this fix, to use '*data' everywhere 'net->sctp.probe_interval' is
used.

## References
- https://git.kernel.org/stable/c/1dc5da6c4178f3e4b95c631418f72de9f86c0449
- https://git.kernel.org/stable/c/284a221f8fa503628432c7bb5108277c688c6ffa
- https://git.kernel.org/stable/c/44ee8635922b6eb940faddb961a8347c6857d722
- https://git.kernel.org/stable/c/6259d2484d0ceff42245d1f09cc8cb6ee72d847a
- https://git.kernel.org/stable/c/bcf8c60074e81ed2ac2d35130917175a3949c917
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21636.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21636
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
