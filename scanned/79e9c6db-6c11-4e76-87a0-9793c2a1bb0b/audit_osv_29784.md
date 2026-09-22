# [H] nvmet-tcp: fix kernel crash if commands allocation fails

## Summary
Severity: High
Advisory: CVE-2024-46737
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-09-18
Source: https://osv.dev/vulnerability/CVE-2024-46737
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.0.0 <5.4.284, >=5.5.0 <5.10.226, >=5.11.0 <5.15.167, >=5.16.0 <6.1.110, >=6.2.0 <6.6.51, >=6.7.0 <6.10.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

nvmet-tcp: fix kernel crash if commands allocation fails

If the commands allocation fails in nvmet_tcp_alloc_cmds()
the kernel crashes in nvmet_tcp_release_queue_work() because of
a NULL pointer dereference.

  nvmet: failed to install queue 0 cntlid 1 ret 6
  Unable to handle kernel NULL pointer dereference at
         virtual address 0000000000000008

Fix the bug by setting queue->nr_cmds to zero in case
nvmet_tcp_alloc_cmd() fails.

## References
- https://git.kernel.org/stable/c/03e1fd0327fa5e2174567f5fe9290fe21d21b8f4
- https://git.kernel.org/stable/c/489f2913a63f528cfe3f21722583fb981967ecda
- https://git.kernel.org/stable/c/50632b877ce55356f5d276b9add289b1e7ddc683
- https://git.kernel.org/stable/c/5572a55a6f830ee3f3a994b6b962a5c327d28cb3
- https://git.kernel.org/stable/c/6c04d1e3ab22cc5394ef656429638a5947f87244
- https://git.kernel.org/stable/c/7957c731fc2b23312f8935812dee5a0b14b04e2d
- https://git.kernel.org/stable/c/91dad30c5607e62864f888e735d0965567827bdf
- https://lists.debian.org/debian-lts-announce/2024/10/msg00003.html
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/46xxx/CVE-2024-46737.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-46737
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
