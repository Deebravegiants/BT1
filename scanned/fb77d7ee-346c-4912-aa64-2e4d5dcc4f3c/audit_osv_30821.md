# [H] jfs: fix shift-out-of-bounds in dbSplit

## Summary
Severity: High
Advisory: CVE-2024-56597
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-12-27
Source: https://osv.dev/vulnerability/CVE-2024-56597
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <5.4.287, >=5.5.0 <5.10.231, >=5.11.0 <5.15.174, >=5.16.0 <6.1.120, >=6.2.0 <6.6.66, >=6.7.0 <6.12.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

jfs: fix shift-out-of-bounds in dbSplit

When dmt_budmin is less than zero, it causes errors
in the later stages. Added a check to return an error beforehand
in dbAllocCtl itself.

## References
- https://git.kernel.org/stable/c/51a203470f502a64a3da8dcea51c4748e8267a6c
- https://git.kernel.org/stable/c/52756a57e978e2706543a254f88f266cc6702f36
- https://git.kernel.org/stable/c/6676034aa753aa448beb30dbd75630927ba7cd96
- https://git.kernel.org/stable/c/a5f5e4698f8abbb25fe4959814093fb5bfa1aa9d
- https://git.kernel.org/stable/c/bbb24ce7f06ef9b7c05beb9340787cbe9fd3d08e
- https://git.kernel.org/stable/c/c56245baf3fd1f79145dd7408e3ead034b74255c
- https://git.kernel.org/stable/c/df7c76636952670b31bd6c12b3aed3c502122273
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56597.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56597
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
