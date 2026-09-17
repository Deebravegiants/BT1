# [M] ALSA: firewire-lib: Avoid division by zero in apply_constraint_to_size()

## Summary
Severity: Medium
Advisory: CVE-2024-50205
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-11-08
Source: https://osv.dev/vulnerability/CVE-2024-50205
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.20.0 <5.4.285, >=5.5.0 <5.10.229, >=5.11.0 <5.15.170, >=5.16.0 <6.1.115, >=6.2.0 <6.6.59, >=6.7.0 <6.11.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

ALSA: firewire-lib: Avoid division by zero in apply_constraint_to_size()

The step variable is initialized to zero. It is changed in the loop,
but if it's not changed it will remain zero. Add a variable check
before the division.

The observed behavior was introduced by commit 826b5de90c0b
("ALSA: firewire-lib: fix insufficient PCM rule for period/buffer size"),
and it is difficult to show that any of the interval parameters will
satisfy the snd_interval_test() condition with data from the
amdtp_rate_table[] table.

Found by Linux Verification Center (linuxtesting.org) with SVACE.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://git.kernel.org/stable/c/3452d39c4704aa12504e4190298c721fb01083c3
- https://git.kernel.org/stable/c/4bdc21506f12b2d432b1f2667e5ff4c75eee58e3
- https://git.kernel.org/stable/c/5e431f85c87bbffd93a9830d5a576586f9855291
- https://git.kernel.org/stable/c/72cafe63b35d06b5cfbaf807e90ae657907858da
- https://git.kernel.org/stable/c/7d4eb9e22131ec154e638cbd56629195c9bcbe9a
- https://git.kernel.org/stable/c/d2826873db70a6719cdd9212a6739f3e6234cfc4
- https://git.kernel.org/stable/c/d575414361630b8b0523912532fcd7c79e43468c
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50205.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50205
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
