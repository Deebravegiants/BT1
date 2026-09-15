# [H] CVE-2016-1248

## Summary
Severity: High
Advisory: CVE-2016-1248
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2016-11-23
Source: https://osv.dev/vulnerability/CVE-2016-1248
Type: osv

## Details
vim before patch 8.0.0056 does not properly validate values for the 'filetype', 'syntax' and 'keymap' options, which may result in the execution of arbitrary code if a file with a specially crafted modeline is opened.

## References
- http://www.securityfocus.com/bid/94478
- http://www.securitytracker.com/id/1037338
- http://rhn.redhat.com/errata/RHSA-2016-2972.html
- http://www.debian.org/security/2016/dsa-3722
- http://www.ubuntu.com/usn/USN-3139-1
- https://lists.debian.org/debian-lts-announce/2016/11/msg00025.html
- https://lists.debian.org/debian-security-announce/2016/msg00305.html
- https://security.gentoo.org/glsa/201701-29
- http://openwall.com/lists/oss-security/2016/11/22/20
- https://anonscm.debian.org/cgit/pkg-vim/vim.git/tree/debian/changelog
- https://github.com/neovim/neovim/commit/4fad66fbe637818b6b3d6bc5d21923ba72795040
- https://github.com/vim/vim/commit/d0b5138ba4bccff8a744c99836041ef6322ed39a
- https://github.com/vim/vim/releases/tag/v8.0.0056
