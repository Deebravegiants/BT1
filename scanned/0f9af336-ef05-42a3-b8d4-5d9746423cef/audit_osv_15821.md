# [M] CVE-2019-19922

## Summary
Severity: Medium
Advisory: CVE-2019-19922
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-12-22
Source: https://osv.dev/vulnerability/CVE-2019-19922
Type: osv

## Details
kernel/sched/fair.c in the Linux kernel before 5.3.9, when cpu.cfs_quota_us is used (e.g., with Kubernetes), allows attackers to cause a denial of service against non-cpu-bound applications by generating a workload that triggers unwanted slice expiration, aka CID-de53fd7aedb1. (In other words, although this slice expiration would typically be seen with benign workloads, it is possible that an attacker could calculate how many stray requests are required to force an entire Kubernetes cluster into a low-performance state caused by slice expiration, and ensure that a DDoS attack sent that number of stray requests. An attack does not affect the stability of the kernel; it only causes mismanagement of application execution.)

## References
- https://lists.debian.org/debian-lts-announce/2020/01/msg00013.html
- https://usn.ubuntu.com/4226-1/
- https://security.netapp.com/advisory/ntap-20200204-0002/
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.3.9
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=de53fd7aedb100f03e5d2231cfce0e4993282425
- https://github.com/kubernetes/kubernetes/issues/67577
- https://github.com/torvalds/linux/commit/de53fd7aedb100f03e5d2231cfce0e4993282425
- https://www.oracle.com/security-alerts/cpuApr2021.html
- https://relistan.com/the-kernel-may-be-slowing-down-your-app
