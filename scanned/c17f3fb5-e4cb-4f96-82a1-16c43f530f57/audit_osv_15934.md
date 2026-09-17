# [M] CVE-2019-20807

## Summary
Severity: Medium
Advisory: CVE-2019-20807
CVSS: 5.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L)
Published: 2020-05-28
Source: https://osv.dev/vulnerability/CVE-2019-20807
Type: osv

## Details
In Vim before 8.1.0881, users can circumvent the rvim restricted mode and execute arbitrary OS commands via scripting interfaces (e.g., Python, Ruby, or Lua).

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-06/msg00018.html
- http://seclists.org/fulldisclosure/2020/Jul/24
- https://github.com/vim/vim/releases/tag/v8.1.0881
- https://lists.debian.org/debian-lts-announce/2022/01/msg00003.html
- https://support.apple.com/kb/HT211289
- https://usn.ubuntu.com/4582-1/
- https://www.starwindsoftware.com/security/sw-20220812-0003/
- https://github.com/vim/vim/commit/8c62a08faf89663e5633dc5036cd8695c80f1075
