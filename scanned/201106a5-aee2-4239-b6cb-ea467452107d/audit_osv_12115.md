# [H] CVE-2018-10361

## Summary
Severity: High
Advisory: CVE-2018-10361
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-04-25
Source: https://osv.dev/vulnerability/CVE-2018-10361
Type: osv

## Details
An issue was discovered in KTextEditor 5.34.0 through 5.45.0. Insecure handling of temporary files in the KTextEditor's kauth_ktexteditor_helper service (as utilized in the Kate text editor) can allow other unprivileged users on the local system to gain root privileges. The attack occurs when one user (who has an unprivileged account but is also able to authenticate as root) writes a text file using Kate into a directory owned by a another unprivileged user. The latter unprivileged user conducts a symlink attack to achieve privilege escalation.

## References
- http://www.openwall.com/lists/oss-security/2019/07/09/3
- http://www.openwall.com/lists/oss-security/2018/04/24/1
- https://bugzilla.suse.com/show_bug.cgi?id=1033055
