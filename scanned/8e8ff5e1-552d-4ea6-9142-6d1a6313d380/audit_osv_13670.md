# [H] CVE-2018-20786

## Summary
Severity: High
Advisory: CVE-2018-20786
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-02-24
Source: https://osv.dev/vulnerability/CVE-2018-20786
Type: osv

## Details
libvterm through 0+bzr726, as used in Vim and other products, mishandles certain out-of-memory conditions, leading to a denial of service (application crash), related to screen.c, state.c, and vterm.c.

## References
- https://usn.ubuntu.com/4309-1/
- https://github.com/vim/vim/commit/cd929f7ba8cc5b6d6dcf35c8b34124e969fed6b8
- https://github.com/vim/vim/issues/3711
