# [H] CVE-2021-3493

## Summary
Severity: High
Advisory: CVE-2021-3493
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-04-17
Source: https://osv.dev/vulnerability/CVE-2021-3493
Type: osv

## Details
The overlayfs implementation in the linux kernel did not properly validate with respect to user namespaces the setting of file capabilities on files in an underlying file system. Due to the combination of unprivileged user namespaces along with a patch carried in the Ubuntu kernel to allow unprivileged overlay mounts, an attacker could use this to gain elevated privileges.

## References
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2021-3493
- https://ubuntu.com/security/notices/USN-4917-1
- https://www.openwall.com/lists/oss-security/2021/04/16/1
- http://packetstormsecurity.com/files/162866/Ubuntu-OverlayFS-Local-Privilege-Escalation.html
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=7c03e2cda4a584cadc398e8f6641ca9988a39d52
- http://packetstormsecurity.com/files/162434/Kernel-Live-Patch-Security-Notice-LSN-0076-1.html
- http://packetstormsecurity.com/files/165151/Ubuntu-Overlayfs-Local-Privilege-Escalation.html
