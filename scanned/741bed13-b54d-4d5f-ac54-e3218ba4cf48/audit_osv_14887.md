# [H] CVE-2019-12209

## Summary
Severity: High
Advisory: CVE-2019-12209
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-06-04
Source: https://osv.dev/vulnerability/CVE-2019-12209
Type: osv

## Details
Yubico pam-u2f 1.0.7 attempts parsing of the configured authfile (default $HOME/.config/Yubico/u2f_keys) as root (unless openasuser was enabled), and does not properly verify that the path lacks symlinks pointing to other files on the system owned by root. If the debug option is enabled in the PAM configuration, part of the file contents of a symlink target will be logged, possibly revealing sensitive information.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-07/msg00012.html
- http://lists.opensuse.org/opensuse-security-announce/2019-07/msg00018.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/5FOR4ADC356JPCHAJI5UXZORLC3VNBPS/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ZCGU6UQLI3ZTW3UYCTMQW7VDL5M4LCWR/
- https://developers.yubico.com/pam-u2f/Release_Notes.html
- https://github.com/Yubico/pam-u2f/commit/7db3386fcdb454e33a3ea30dcfb8e8960d4c3aa3
- http://www.openwall.com/lists/oss-security/2019/06/05/1
