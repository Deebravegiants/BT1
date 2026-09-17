# [H] fs: drop peer group ids under namespace lock

## Summary
Severity: High
Advisory: CVE-2023-54128
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-24
Source: https://osv.dev/vulnerability/CVE-2023-54128
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.12.0 <5.15.107, >=5.16.0 <6.1.24, >=6.2.0 <6.2.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

fs: drop peer group ids under namespace lock

When cleaning up peer group ids in the failure path we need to make sure
to hold on to the namespace lock. Otherwise another thread might just
turn the mount from a shared into a non-shared mount concurrently.

## References
- https://git.kernel.org/stable/c/0af8fae81d8b7f1beddc17c5d4cfa43235134648
- https://git.kernel.org/stable/c/65c324d3f35c05e37afec39ac80743583fdcc96c
- https://git.kernel.org/stable/c/cb2239c198ad9fbd5aced22cf93e45562da781eb
- https://git.kernel.org/stable/c/ddca03d97daa7b07b60c52e3d3060762732c6666
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/54xxx/CVE-2023-54128.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-54128
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
