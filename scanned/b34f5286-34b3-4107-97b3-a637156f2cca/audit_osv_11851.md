# [C] CVE-2018-0502

## Summary
Severity: Critical
Advisory: CVE-2018-0502
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-09-05
Source: https://osv.dev/vulnerability/CVE-2018-0502
Type: osv

## Details
An issue was discovered in zsh before 5.6. The beginning of a #! script file was mishandled, potentially leading to an execve call to a program named on the second line.

## References
- https://lists.debian.org/debian-lts-announce/2020/12/msg00000.html
- https://security.gentoo.org/glsa/201903-02
- https://usn.ubuntu.com/3764-1/
- https://www.zsh.org/mla/zsh-announce/136
- https://bugs.debian.org/908000
- https://sourceforge.net/p/zsh/code/ci/1c4c7b6a4d17294df028322b70c53803a402233d
