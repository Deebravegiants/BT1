# [H] memstick/mspro_block: fix handling of read-only devices

## Summary
Severity: High
Advisory: CVE-2022-49178
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49178
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.25 <5.16.19, >=5.17.0 <5.17.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

memstick/mspro_block: fix handling of read-only devices

Use set_disk_ro to propagate the read-only state to the block layer
instead of checking for it in ->open and leaking a reference in case
of a read-only device.

## References
- https://git.kernel.org/stable/c/057b53c4f87690d626203acef8b63d52a9bf2f43
- https://git.kernel.org/stable/c/6a0725b9d78ff6efdc95a37e4f05072e79c63918
- https://git.kernel.org/stable/c/6dab421bfe06a59bf8f212a72e34673e8acf2018
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49178.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49178
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
