# [M] CVE-2017-12192

## Summary
Severity: Medium
Advisory: CVE-2017-12192
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-10-12
Source: https://osv.dev/vulnerability/CVE-2017-12192
Type: osv

## Details
The keyctl_read_key function in security/keys/keyctl.c in the Key Management subcomponent in the Linux kernel before 4.13.5 does not properly consider that a key may be possessed but negatively instantiated, which allows local users to cause a denial of service (OOPS and system crash) via a crafted KEYCTL_READ operation.

## References
- https://usn.ubuntu.com/3583-1/
- https://usn.ubuntu.com/3583-2/
- https://lkml.org/lkml/2017/9/18/764
- http://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.13.5
- https://access.redhat.com/errata/RHSA-2018:0151
- https://bugzilla.redhat.com/show_bug.cgi?id=1493435
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=37863c43b2c6464f252862bf2e9768264e961678
- https://github.com/torvalds/linux/commit/37863c43b2c6464f252862bf2e9768264e961678
