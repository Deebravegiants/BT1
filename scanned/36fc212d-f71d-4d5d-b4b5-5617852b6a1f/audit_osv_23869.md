# [M] tcp: Fix data-races around sysctl_tcp_min_snd_mss.

## Summary
Severity: Medium
Advisory: CVE-2022-49596
Ecosystem: Linux
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49596
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.2.0 <5.4.208, >=5.5.0 <5.10.134, >=5.11.0 <5.15.58, >=5.16.0 <5.18.15

## Details
In the Linux kernel, the following vulnerability has been resolved:

tcp: Fix data-races around sysctl_tcp_min_snd_mss.

While reading sysctl_tcp_min_snd_mss, it can be changed concurrently.
Thus, we need to add READ_ONCE() to its readers.

## References
- https://git.kernel.org/stable/c/0d8a39feb58910a7f7746b1770ee5578cc551fe6
- https://git.kernel.org/stable/c/0fc9357282df055e30990b29f4b7afa53ab42cdb
- https://git.kernel.org/stable/c/78eb166cdefcc3221c8c7c1e2d514e91a2eb5014
- https://git.kernel.org/stable/c/97992e8feff33b3ae154a113ec398546bbacda80
- https://git.kernel.org/stable/c/fdb96b69f5909ffcdd6f1e0902219fc6d7689ff7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49596.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49596
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
