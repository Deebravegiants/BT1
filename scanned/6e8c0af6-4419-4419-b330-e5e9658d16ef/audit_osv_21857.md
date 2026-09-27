# [H] CVE-2022-0492

## Summary
Severity: High
Advisory: CVE-2022-0492
Aliases: A-224859358, PUB-A-224859358
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-03-03
Source: https://osv.dev/vulnerability/CVE-2022-0492
Type: osv

## Details
A vulnerability was found in the Linux kernel’s cgroup_release_agent_write in the kernel/cgroup/cgroup-v1.c function. This flaw, under certain circumstances, allows the use of the cgroups v1 release_agent feature to escalate privileges and bypass the namespace isolation unexpectedly.

## References
- http://packetstormsecurity.com/files/166444/Kernel-Live-Patch-Security-Notice-LSN-0085-1.html
- http://packetstormsecurity.com/files/167386/Kernel-Live-Patch-Security-Notice-LSN-0086-1.html
- http://packetstormsecurity.com/files/176099/Docker-cgroups-Container-Escape.html
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=24f6008564183aa120d07c03d9289519c2fe02af
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2022-0492
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/0xxx/CVE-2022-0492.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-0492
- https://security.netapp.com/advisory/ntap-20220419-0002/
- https://www.debian.org/security/2022/dsa-5095
- https://www.debian.org/security/2022/dsa-5096
- https://bugzilla.redhat.com/show_bug.cgi?id=2051505
- https://lists.debian.org/debian-lts-announce/2022/03/msg00011.html
- https://lists.debian.org/debian-lts-announce/2022/03/msg00012.html
