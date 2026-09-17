# [C] netfilter: conntrack: re-fetch conntrack after insertion

## Summary
Severity: Critical
Advisory: CVE-2022-49561
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49561
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.7.0 <4.14.282, >=4.15.0 <4.19.246, >=4.20.0 <5.4.197, >=5.5.0 <5.10.120, >=5.11.0 <5.15.45, >=5.16.0 <5.17.13, >=5.18.0 <5.18.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: conntrack: re-fetch conntrack after insertion

In case the conntrack is clashing, insertion can free skb->_nfct and
set skb->_nfct to the already-confirmed entry.

This wasn't found before because the conntrack entry and the extension
space used to free'd after an rcu grace period, plus the race needs
events enabled to trigger.

## References
- https://git.kernel.org/stable/c/01989d7eebb61c99bd4b88ebc8e261bd2f02caed
- https://git.kernel.org/stable/c/04e4a11dc723c52db7a36dc58f0d69ce6426f8f0
- https://git.kernel.org/stable/c/04f9e9104c969d8ce10a4a43634f641ed082092d
- https://git.kernel.org/stable/c/56b14ecec97f39118bf85c9ac2438c5a949509ed
- https://git.kernel.org/stable/c/91a36ec160ec1a0c8f5352b772dffcbb0b6023e3
- https://git.kernel.org/stable/c/92a999d1963eed0df666284e20055136ceabd12f
- https://git.kernel.org/stable/c/b16bb373988da3ceb0308381634117e18b6ec60d
- https://git.kernel.org/stable/c/e97222b785e70e8973281666d709baad6523d8af
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49561.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49561
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
