# [C] CVE-2025-32463

## Summary
Severity: Critical
Advisory: CVE-2025-32463
CVSS: 9.3 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2025-06-30
Source: https://osv.dev/vulnerability/CVE-2025-32463
Type: osv

## Details
Sudo before 1.9.17p1 allows local users to obtain root access because /etc/nsswitch.conf from a user-controlled directory is used with the --chroot option.

## References
- https://access.redhat.com/security/cve/cve-2025-32463
- https://bugs.gentoo.org/show_bug.cgi?id=CVE-2025-32463
- https://explore.alas.aws.amazon.com/CVE-2025-32463.html
- https://security-tracker.debian.org/tracker/CVE-2025-32463
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2025-32463
- https://www.openwall.com/lists/oss-security/2025/06/30/3
- https://www.stratascale.com/vulnerability-alert-CVE-2025-32463-sudo-chroot
- https://www.sudo.ws/releases/changelog/
- https://www.suse.com/security/cve/CVE-2025-32463.html
- https://www.suse.com/support/update/announcement/2025/suse-su-202502177-1/
- https://www.vicarius.io/vsociety/posts/cve-2025-32463-detect-sudo-vulnerability
- https://www.vicarius.io/vsociety/posts/cve-2025-32463-mitigate-sudo-vulnerability
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/32xxx/CVE-2025-32463.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-32463
- https://ubuntu.com/security/notices/USN-7604-1
- https://www.sudo.ws/security/advisories/
- https://www.sudo.ws/security/advisories/chroot_bug/
- https://www.secpod.com/blog/sudo-lpe-vulnerabilities-resolved-what-you-need-to-know-about-cve-2025-32462-and-cve-2025-32463/
- https://iototsecnews.jp/2025/07/01/linux-sudo-chroot-vulnerability-enables-hackers-to-elevate-privileges-to-root/
