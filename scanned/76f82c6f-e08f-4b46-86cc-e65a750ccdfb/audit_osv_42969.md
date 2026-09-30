# [H] selinux: check connect-related permissions on TCP Fast Open

## Summary
Severity: High
Advisory: CVE-2026-72243
Ecosystem: Linux
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:N)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72243
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.6.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

selinux: check connect-related permissions on TCP Fast Open

Similar to Landlock, SELinux was not updated when TCP Fast Open
support was introduced to ensure connect-related permissions are
checked when using TCP Fast Open. Update its socket_sendmsg() hook to
call selinux_socket_connect() when MSG_FASTOPEN is passed.

## References
- https://git.kernel.org/stable/c/11406d0d7e11b4e525bb2ace2c70107031d058da
- https://git.kernel.org/stable/c/44c74d27d1b9aaa99fa8a83640c1223575262b80
- https://git.kernel.org/stable/c/646ebbc5f2ff9147d084e1213143f091026a611c
- https://git.kernel.org/stable/c/d028bc080a0dcd6a7f8e1ae1bd32dda696505ba3
- https://git.kernel.org/stable/c/e507633bf76bccf1a6af27771fb0d6e2862b7eac
- https://git.kernel.org/stable/c/fc633a598206d4f23af782db7c0b5f3a82751d2c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72243.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72243
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
