# [H] CVE-2022-30550

## Summary
Severity: High
Advisory: CVE-2022-30550
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-07-17
Source: https://osv.dev/vulnerability/CVE-2022-30550
Type: osv

## Details
An issue was discovered in the auth component in Dovecot 2.2 and 2.3 before 2.3.20. When two passdb configuration entries exist with the same driver and args settings, incorrect username_filter and mechanism settings can be applied to passdb definitions. These incorrectly applied settings can lead to an unintended security configuration and can permit privilege escalation in certain configurations. The documentation does not advise against the use of passdb definitions that have the same driver and args settings. One such configuration would be where an administrator wishes to use the same PAM configuration or passwd file for both normal and master users but use the username_filter setting to restrict which of the users is able to be a master user.

## References
- https://dovecot.org/security
- https://www.dovecot.org/download/
- https://www.openwall.com/lists/oss-security/2022/07/08/1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/30xxx/CVE-2022-30550.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-30550
- https://security.gentoo.org/glsa/202310-19
- https://lists.debian.org/debian-lts-announce/2022/09/msg00032.html
