# [C] CVE-2016-10150

## Summary
Severity: Critical
Advisory: CVE-2016-10150
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-02-06
Source: https://osv.dev/vulnerability/CVE-2016-10150
Type: osv

## Details
Use-after-free vulnerability in the kvm_ioctl_create_device function in virt/kvm/kvm_main.c in the Linux kernel before 4.8.13 allows host OS users to cause a denial of service (host OS crash) or possibly gain privileges via crafted ioctl calls on the /dev/kvm device.

## References
- http://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.8.13
- http://www.securityfocus.com/bid/95672
- http://www.openwall.com/lists/oss-security/2017/01/18/10
- https://bugzilla.redhat.com/show_bug.cgi?id=1414506
- https://github.com/torvalds/linux/commit/a0f1d21c1ccb1da66629627a74059dd7f5ac9c61
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=a0f1d21c1ccb1da66629627a74059dd7f5ac9c61
