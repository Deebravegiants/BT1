# [H] block: disable the elevator int del_gendisk

## Summary
Severity: High
Advisory: CVE-2022-49694
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49694
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.16.0 <5.18.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

block: disable the elevator int del_gendisk

The elevator is only used for file system requests, which are stopped in
del_gendisk.  Move disabling the elevator and freeing the scheduler tags
to the end of del_gendisk instead of doing that work in disk_release and
blk_cleanup_queue to avoid a use after free on q->tag_set from
disk_release as the tag_set might not be alive at that point.

Move the blk_qos_exit call as well, as it just depends on the elevator
exit and would be the only reason to keep the not exactly cheap queue
freeze in disk_release.

## References
- https://git.kernel.org/stable/c/50e34d78815e474d410f342fbe783b18192ca518
- https://git.kernel.org/stable/c/f28699fafc047ec33299da01e928c3a0073c5cc6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49694.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49694
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
