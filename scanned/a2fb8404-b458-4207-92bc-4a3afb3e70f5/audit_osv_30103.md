# [H] ntb: ntb_hw_switchtec: Fix use after free vulnerability in switchtec_ntb_remove due to race condition

## Summary
Severity: High
Advisory: CVE-2024-50059
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-10-21
Source: https://osv.dev/vulnerability/CVE-2024-50059
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.16.0 <5.4.285, >=5.5.0 <5.10.227, >=5.11.0 <5.15.168, >=5.16.0 <6.1.113, >=6.2.0 <6.6.57, >=6.7.0 <6.11.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

ntb: ntb_hw_switchtec: Fix use after free vulnerability in switchtec_ntb_remove due to race condition

In the switchtec_ntb_add function, it can call switchtec_ntb_init_sndev
function, then &sndev->check_link_status_work is bound with
check_link_status_work. switchtec_ntb_link_notification may be called
to start the work.

If we remove the module which will call switchtec_ntb_remove to make
cleanup, it will free sndev through kfree(sndev), while the work
mentioned above will be used. The sequence of operations that may lead
to a UAF bug is as follows:

CPU0                                 CPU1

                        | check_link_status_work
switchtec_ntb_remove    |
kfree(sndev);           |
                        | if (sndev->link_force_down)
                        | // use sndev

Fix it by ensuring that the work is canceled before proceeding with
the cleanup in switchtec_ntb_remove.

## References
- https://git.kernel.org/stable/c/177925d9c8715a897bb79eca62628862213ba956
- https://git.kernel.org/stable/c/3ae45be8492460a35b5aebf6acac1f1d32708946
- https://git.kernel.org/stable/c/5126d8f5567f49b52e21fca320eaa97977055099
- https://git.kernel.org/stable/c/92728fceefdaa2a0a3aae675f86193b006eeaa43
- https://git.kernel.org/stable/c/b650189687822b705711f0567a65a164a314d8df
- https://git.kernel.org/stable/c/e51aded92d42784313ba16c12f4f88cc4f973bbb
- https://git.kernel.org/stable/c/fa840ba4bd9f3bad7f104e5b32028ee73af8b3dd
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50059.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50059
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
