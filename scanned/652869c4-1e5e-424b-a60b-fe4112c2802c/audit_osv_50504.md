# [H] CVE-2020-16119

## Summary
Severity: High
Advisory: CVE-2020-16119
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-01-14
Source: https://osv.dev/vulnerability/CVE-2020-16119
Type: osv

## Details
Use-after-free vulnerability in the Linux kernel exploitable by a local attacker due to reuse of a DCCP socket with an attached dccps_hc_tx_ccid object as a listener after being released. Fixed in Ubuntu Linux kernel 5.4.0-51.56, 5.3.0-68.63, 4.15.0-121.123, 4.4.0-193.224, 3.13.0.182.191 and 3.2.0-149.196.

## References
- https://lore.kernel.org/netdev/20201013171849.236025-1-kleber.souza%40canonical.com/T/
- https://lists.debian.org/debian-lts-announce/2021/10/msg00010.html
- https://lists.debian.org/debian-lts-announce/2021/12/msg00012.html
- https://security.netapp.com/advisory/ntap-20210304-0006/
- https://ubuntu.com/USN-4577-1
- https://ubuntu.com/USN-4578-1
- https://ubuntu.com/USN-4576-1
- https://ubuntu.com/USN-4579-1
- https://ubuntu.com/USN-4580-1
- https://www.debian.org/security/2021/dsa-4978
- https://git.launchpad.net/~ubuntu-kernel/ubuntu/+source/linux/+git/focal/commit/?id=01872cb896c76cedeabe93a08456976ab55ad695
- https://launchpad.net/bugs/1883840
