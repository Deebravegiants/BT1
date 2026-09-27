# [H] netfilter: nf_conncount: fix leaked ct in error paths

## Summary
Severity: High
Advisory: CVE-2025-71146
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-01-23
Source: https://osv.dev/vulnerability/CVE-2025-71146
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.12.63 <6.12.64, >=6.18.2 <6.18.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: nf_conncount: fix leaked ct in error paths

There are some situations where ct might be leaked as error paths are
skipping the refcounted check and return immediately. In order to solve
it make sure that the check is always called.

## References
- https://git.kernel.org/stable/c/08fa37f4c8c59c294e9c18fea2d083ee94074e5a
- https://git.kernel.org/stable/c/0b88be7211d21a0d68bb1e56dc805944e3654d6f
- https://git.kernel.org/stable/c/2e2a720766886190a6d35c116794693aabd332b6
- https://git.kernel.org/stable/c/325eb61bb30790ea27782203a17b007ce1754a67
- https://git.kernel.org/stable/c/4bd2b89f4028f250dd1c1625eb3da1979b04a5e8
- https://git.kernel.org/stable/c/e1ac8dce3a893641bef224ad057932f142b8a36f
- https://git.kernel.org/stable/c/f381a33f34dda9e4023e38ba68c943bca83245e9
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/71xxx/CVE-2025-71146.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-71146
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
