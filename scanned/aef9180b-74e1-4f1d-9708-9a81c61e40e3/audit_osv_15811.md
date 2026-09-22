# [H] CVE-2019-19882

## Summary
Severity: High
Advisory: CVE-2019-19882
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-12-18
Source: https://osv.dev/vulnerability/CVE-2019-19882
Type: osv

## Details
shadow 4.8, in certain circumstances affecting at least Gentoo, Arch Linux, and Void Linux, allows local users to obtain root access because setuid programs are misconfigured. Specifically, this affects shadow 4.8 when compiled using --with-libpam but without explicitly passing --disable-account-tools-setuid, and without a PAM configuration suitable for use with setuid account management tools. This combination leads to account management tools (groupadd, groupdel, groupmod, useradd, userdel, usermod) that can easily be used by unprivileged local users to escalate privileges to root in multiple ways. This issue became much more relevant in approximately December 2019 when an unrelated bug was fixed (i.e., the chmod calls to suidusbins were fixed in the upstream Makefile which is now included in the release version 4.8).

## References
- https://security.gentoo.org/glsa/202008-09
- https://github.com/shadow-maint/shadow/commit/edf7547ad5aa650be868cf2dac58944773c12d75
- https://github.com/shadow-maint/shadow/pull/199
- https://github.com/void-linux/void-packages/pull/17580
- https://bugs.archlinux.org/task/64836
- https://bugs.gentoo.org/702252
