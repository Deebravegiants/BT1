# [H] CVE-2021-4154

## Summary
Severity: High
Advisory: CVE-2021-4154
Aliases: A-218836280, ASB-A-218836280
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2022-02-04
Source: https://osv.dev/vulnerability/CVE-2021-4154
Type: osv

## Details
A use-after-free flaw was found in cgroup1_parse_param in kernel/cgroup/cgroup-v1.c in the Linux kernel's cgroup v1 parser. A local attacker with a user privilege could cause a privilege escalation by exploiting the fsconfig syscall parameter leading to a container breakout and a denial of service on the system.

## References
- https://cloud.google.com/anthos/clusters/docs/security-bulletins#gcp-2022-002
- https://security.netapp.com/advisory/ntap-20220225-0004/
- https://bugzilla.redhat.com/show_bug.cgi?id=2034514
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=3b0462726e7ef281c35a7a4ae33e93ee2bc9975b
