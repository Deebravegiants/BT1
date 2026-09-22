# [M] CVE-2009-1142

## Summary
Severity: Medium
Advisory: CVE-2009-1142
CVSS: 6.7 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-11-23
Source: https://osv.dev/vulnerability/CVE-2009-1142
Type: osv

## Details
An issue was discovered in open-vm-tools 2009.03.18-154848. Local users can gain privileges via a symlink attack on /tmp files if vmware-user-suid-wrapper is setuid root and the ChmodChownDirectory function is enabled.

## References
- https://bugs.gentoo.org/264577
- https://github.com/vmware/open-vm-tools/releases/tag/2009.03.18-154848
- https://bugs.gentoo.org/264577
