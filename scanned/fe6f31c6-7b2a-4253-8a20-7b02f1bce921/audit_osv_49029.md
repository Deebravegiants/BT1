# [H] CVE-2018-20669

## Summary
Severity: High
Advisory: CVE-2018-20669
Aliases: A-135368228, ASB-A-135368228
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-03-21
Source: https://osv.dev/vulnerability/CVE-2018-20669
Type: osv

## Details
An issue where a provided address with access_ok() is not checked was discovered in i915_gem_execbuffer2_ioctl in drivers/gpu/drm/i915/i915_gem_execbuffer.c in the Linux kernel through 4.19.13. A local attacker can craft a malicious IOCTL function call to overwrite arbitrary kernel memory, resulting in a Denial of Service or privilege escalation.

## References
- https://support.f5.com/csp/article/K32059550
- https://usn.ubuntu.com/4485-1/
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/log/drivers/gpu/drm/i915/i915_gem_execbuffer.c
- http://lists.opensuse.org/opensuse-security-announce/2019-02/msg00042.html
- http://www.securityfocus.com/bid/106748
- https://access.redhat.com/security/cve/cve-2018-20669
- https://security.netapp.com/advisory/ntap-20190404-0002/
- http://www.openwall.com/lists/oss-security/2019/01/23/6
