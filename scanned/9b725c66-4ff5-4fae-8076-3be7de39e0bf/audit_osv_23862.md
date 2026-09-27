# [M] tcp: Fix data-races around sysctl_tcp_migrate_req.

## Summary
Severity: Medium
Advisory: CVE-2022-49588
Ecosystem: Linux
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49588
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.14.0 <5.15.58, >=5.16.0 <5.18.15

## Details
In the Linux kernel, the following vulnerability has been resolved:

tcp: Fix data-races around sysctl_tcp_migrate_req.

While reading sysctl_tcp_migrate_req, it can be changed concurrently.
Thus, we need to add READ_ONCE() to its readers.

## References
- https://git.kernel.org/stable/c/4177f545895b1da08447a80692f30617154efa6e
- https://git.kernel.org/stable/c/6e569a11eea20a1ccebc3c4e6366bf0574a449e1
- https://git.kernel.org/stable/c/fcf6c6d8aeffebca66f37b17ef1b57112e5e09c1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49588.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49588
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
