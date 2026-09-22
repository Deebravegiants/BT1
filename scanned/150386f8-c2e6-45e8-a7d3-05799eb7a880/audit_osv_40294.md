# [C] batman-adv: fix fragment reassembly length accounting

## Summary
Severity: Critical
Advisory: CVE-2026-52914
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-52914
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.13.0 <5.10.258, >=5.11.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.142, >=6.7.0 <6.12.92, >=6.13.0 <6.18.34, >=6.19.0 <7.0.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

batman-adv: fix fragment reassembly length accounting

batman-adv keeps a running payload length for queued fragments and uses it
to validate a fragment chain before reassembly.

That accounting currently allows the accumulated fragment length to be
truncated during updates. As a result, malformed fragment chains can
bypass the intended validation and drive reassembly with inconsistent
length state, leading to a local denial of service.

Fix the accounting by storing the accumulated length in a length-typed
field and rejecting update overflows before the existing validation logic
runs.

The fix was verified against the original reproducer and against valid
fragment reassembly paths.

## References
- https://git.kernel.org/stable/c/37be61825b15534a16ff9cfc9546de155b6df982
- https://git.kernel.org/stable/c/3eb8bcb823391bd58997831b3c9c152a4ba8e255
- https://git.kernel.org/stable/c/975563c5de1123dde1ec7946bf5556d20c89d74e
- https://git.kernel.org/stable/c/9cd3f16c320bfdadd4509358122368deb56a5741
- https://git.kernel.org/stable/c/e4f3f6b818aa6a678bc54a2d4e0bece2303c6a64
- https://git.kernel.org/stable/c/e910dbf509125fe51ad68e4fa74dc8ab0a8e787a
- https://git.kernel.org/stable/c/f653b040dad1af70fa5cd4fe085e4758925480c9
- https://git.kernel.org/stable/c/fdb2c96efb2baeb3725e9ce3ede8f1e36f5490f0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/52xxx/CVE-2026-52914.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-52914
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
