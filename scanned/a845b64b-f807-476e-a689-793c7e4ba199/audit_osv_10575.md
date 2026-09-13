# [C] CVE-2017-17434

## Summary
Severity: Critical
Advisory: CVE-2017-17434
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-12-06
Source: https://osv.dev/vulnerability/CVE-2017-17434
Type: osv

## Details
The daemon in rsync 3.1.2, and 3.1.3-development before 2017-12-03, does not check for fnamecmp filenames in the daemon_filter_list data structure (in the recv_files function in receiver.c) and also does not apply the sanitize_paths protection mechanism to pathnames found in "xname follows" strings (in the read_ndx_and_attrs function in rsync.c), which allows remote attackers to bypass intended access restrictions.

## References
- https://git.samba.org/?p=rsync.git%3Ba=commit%3Bh=5509597decdbd7b91994210f700329d8a35e70a1
- https://git.samba.org/?p=rsync.git%3Ba=commit%3Bh=70aeb5fddd1b2f8e143276f8d5a085db16c593b9
- https://lists.debian.org/debian-lts-announce/2017/12/msg00020.html
- http://security.cucumberlinux.com/security/details.php?id=170
- https://www.debian.org/security/2017/dsa-4068
