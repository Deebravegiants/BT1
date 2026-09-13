# [H] CVE-2021-3609

## Summary
Severity: High
Advisory: CVE-2021-3609
Aliases: A-223967238, PUB-A-223967238
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-03-03
Source: https://osv.dev/vulnerability/CVE-2021-3609
Type: osv

## Details
.A flaw was found in the CAN BCM networking protocol in the Linux kernel, where a local attacker can abuse a flaw in the CAN subsystem to corrupt memory, crash the system or escalate privileges. This race condition in net/can/bcm.c in the Linux kernel allows for local privilege escalation to root.

## References
- https://security.netapp.com/advisory/ntap-20220419-0004/
- https://www.openwall.com/lists/oss-security/2021/06/19/1
- https://bugzilla.redhat.com/show_bug.cgi?id=1971651
- https://github.com/torvalds/linux/commit/d5f9023fa61ee8b94f37a93f08e94b136cf1e463
- https://github.com/nrb547/kernel-exploitation/blob/main/cve-2021-3609/cve-2021-3609.md
