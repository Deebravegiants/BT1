# [H] libceph: remove debugfs files before client teardown

## Summary
Severity: High
Advisory: CVE-2026-68153
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68153
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.34 <5.10.265, >=5.11.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.148, >=6.7.0 <6.12.101, >=6.13.0 <6.18.42, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

libceph: remove debugfs files before client teardown

ceph_destroy_client() tears down the monitor client before removing
the per-client debugfs files. A concurrent read of the monmap debugfs
file can enter monmap_show() after ceph_monc_stop() has freed
monc->monmap, triggering a use-after-free.

Remove the debugfs files before stopping the OSD and monitor clients.
debugfs_remove() drains active handlers and prevents new accesses, so
the debugfs callbacks can no longer race the rest of client teardown.

## References
- https://git.kernel.org/stable/c/463a264e9094384112a5c8b46f0a9ddaf8566904
- https://git.kernel.org/stable/c/8f5a3abc54ba24dbceb14cc3a719908c4f688091
- https://git.kernel.org/stable/c/ac78549d186090ee7125d28c3a8c376573b36194
- https://git.kernel.org/stable/c/b9fedda2f628e030384228de0dafc574b7fb0c2f
- https://git.kernel.org/stable/c/d3dc8889d39a676bf840132bd5c5c48cb0daba23
- https://git.kernel.org/stable/c/e4c804726c4afce3ba648b982d564f6af2cfa328
- https://git.kernel.org/stable/c/fc1010e7e0204ece6cc0f9af4f473e9553535eab
- https://git.kernel.org/stable/c/fe46b7e06f14f6f94766832df309b249cb689d27
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68153.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68153
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
