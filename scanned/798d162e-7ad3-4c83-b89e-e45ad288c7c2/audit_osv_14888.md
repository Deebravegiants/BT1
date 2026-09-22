# [H] CVE-2019-12210

## Summary
Severity: High
Advisory: CVE-2019-12210
CVSS: 8.1 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2019-06-04
Source: https://osv.dev/vulnerability/CVE-2019-12210
Type: osv

## Details
In Yubico pam-u2f 1.0.7, when configured with debug and a custom debug log file is set using debug_file, that file descriptor is not closed when a new process is spawned. This leads to the file descriptor being inherited into the child process; the child process can then read from and write to it. This can leak sensitive information and also, if written to, be used to fill the disk or plant misinformation.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-07/msg00012.html
- http://lists.opensuse.org/opensuse-security-announce/2019-07/msg00018.html
- https://developers.yubico.com/pam-u2f/Release_Notes.html
- https://github.com/Yubico/pam-u2f/commit/18b1914e32b74ff52000f10e97067e841e5fff62
- http://www.openwall.com/lists/oss-security/2019/06/05/1
