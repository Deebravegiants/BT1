# [H] Use after Free in tc_new_tfilter allowing for privilege escalation in Linux Kernel

## Summary
Severity: High
Advisory: CVE-2022-1055
Aliases: A-228390920, PUB-A-228390920
CVSS: 7.5 (CVSS:4.0/AV:L/AC:H/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:H/SI:H/SA:N)
Published: 2022-03-29
Source: https://osv.dev/vulnerability/CVE-2022-1055
Type: osv

## Details
A use-after-free exists in the Linux Kernel in tc_new_tfilter that could allow a local attacker to gain privilege escalation. The exploit requires unprivileged user namespaces. We recommend upgrading past commit 04c2a47ffb13c29778e2a14e414ad4cb5a5db4b5

## References
- http://packetstormsecurity.com/files/167386/Kernel-Live-Patch-Security-Notice-LSN-0086-1.html
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=04c2a47ffb13c29778e2a14e414ad4cb5a5db4b5
- https://kernel.dance/#04c2a47ffb13c29778e2a14e414ad4cb5a5db4b5
- https://syzkaller.appspot.com/bug?id=2212474c958978ab86525fe6832ac8102c309ffc
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/1xxx/CVE-2022-1055.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-1055
- https://security.netapp.com/advisory/ntap-20220506-0007/
