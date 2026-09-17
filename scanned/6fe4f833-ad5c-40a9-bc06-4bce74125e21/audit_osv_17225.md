# [H] CVE-2020-13881

## Summary
Severity: High
Advisory: CVE-2020-13881
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2020-06-06
Source: https://osv.dev/vulnerability/CVE-2020-13881
Type: osv

## Details
In support.c in pam_tacplus 1.3.8 through 1.5.1, the TACACS+ shared secret gets logged via syslog if the DEBUG loglevel and journald are used.

## References
- https://lists.debian.org/debian-lts-announce/2020/06/msg00007.html
- https://lists.debian.org/debian-lts-announce/2021/08/msg00006.html
- https://usn.ubuntu.com/4521-1/
- https://www.arista.com/en/support/advisories-notices/security-advisories/11705-security-advisory-50
- https://github.com/kravietz/pam_tacplus/issues/149
- http://www.openwall.com/lists/oss-security/2020/06/08/1
- https://github.com/kravietz/pam_tacplus/commit/4a9852c31c2fd0c0e72fbb689a586aabcfb11cb0
