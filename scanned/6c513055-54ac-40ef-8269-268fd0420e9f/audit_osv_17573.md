# [H] CVE-2020-1712

## Summary
Severity: High
Advisory: CVE-2020-1712
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-03-31
Source: https://osv.dev/vulnerability/CVE-2020-1712
Type: osv

## Details
A heap use-after-free vulnerability was found in systemd before version v245-rc1, where asynchronous Polkit queries are performed while handling dbus messages. A local unprivileged attacker can abuse this flaw to crash systemd services or potentially execute code and elevate their privileges, by sending specially crafted dbus messages.

## References
- https://lists.debian.org/debian-lts-announce/2022/06/msg00025.html
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2020-1712
- https://github.com/systemd/systemd/commit/1068447e6954dc6ce52f099ed174c442cb89ed54
- https://github.com/systemd/systemd/commit/637486261528e8aa3da9f26a4487dc254f4b7abb
- https://github.com/systemd/systemd/commit/bc130b6858327b382b07b3985cf48e2aa9016b2d
- https://github.com/systemd/systemd/commit/ea0d0ede03c6f18dbc5036c5e9cccf97e415ccc2
- https://www.openwall.com/lists/oss-security/2020/02/05/1
