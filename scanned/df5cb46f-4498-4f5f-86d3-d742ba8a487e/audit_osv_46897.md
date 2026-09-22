# [M] CVE-2015-7837

## Summary
Severity: Medium
Advisory: CVE-2015-7837
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2017-09-19
Source: https://osv.dev/vulnerability/CVE-2015-7837
Type: osv

## Details
The Linux kernel, as used in Red Hat Enterprise Linux 7, kernel-rt, and Enterprise MRG 2 and when booted with UEFI Secure Boot enabled, allows local users to bypass intended securelevel/secureboot restrictions by leveraging improper handling of secure_boot flag across kexec reboot.

## References
- http://rhn.redhat.com/errata/RHSA-2015-2152.html
- http://rhn.redhat.com/errata/RHSA-2015-2411.html
- http://www.openwall.com/lists/oss-security/2015/10/15/6
- http://www.securityfocus.com/bid/77097
- https://bugzilla.redhat.com/show_bug.cgi?id=1272472
- https://github.com/mjg59/linux/commit/4b2b64d5a6ebc84214755ebccd599baef7c1b798
- http://www.openwall.com/lists/oss-security/2015/10/15/6
- https://bugzilla.redhat.com/show_bug.cgi?id=1272472
- https://github.com/mjg59/linux/commit/4b2b64d5a6ebc84214755ebccd599baef7c1b798
