# [H] CVE-2018-18021

## Summary
Severity: High
Advisory: CVE-2018-18021
CVSS: 7.1 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H)
Published: 2018-10-07
Source: https://osv.dev/vulnerability/CVE-2018-18021
Type: osv

## Details
arch/arm64/kvm/guest.c in KVM in the Linux kernel before 4.18.12 on the arm64 platform mishandles the KVM_SET_ON_REG ioctl. This is exploitable by attackers who can create virtual machines. An attacker can arbitrarily redirect the hypervisor flow of control (with full register control). An attacker can also cause a denial of service (hypervisor panic) via an illegal exception return. This occurs because of insufficient restrictions on userspace access to the core register file, and because PSTATE.M validation does not prevent unintended execution modes.

## References
- https://usn.ubuntu.com/3931-2/
- https://usn.ubuntu.com/3931-1/
- https://usn.ubuntu.com/3821-1/
- https://access.redhat.com/errata/RHSA-2018:3656
- https://usn.ubuntu.com/3821-2/
- https://www.debian.org/security/2018/dsa-4313
- http://www.securityfocus.com/bid/105550
- https://cdn.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.18.12
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=d26c25a9d19b5976b319af528886f89cf455692d
- https://github.com/torvalds/linux/commit/2a3f93459d689d990b3ecfbe782fec89b97d3279
- https://github.com/torvalds/linux/commit/d26c25a9d19b5976b319af528886f89cf455692d
- https://www.openwall.com/lists/oss-security/2018/10/02/2
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=2a3f93459d689d990b3ecfbe782fec89b97d3279
