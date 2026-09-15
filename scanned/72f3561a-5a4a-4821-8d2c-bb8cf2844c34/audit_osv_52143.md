# [M] CVE-2021-47120

## Summary
Severity: Medium
Advisory: CVE-2021-47120
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-03-15
Source: https://osv.dev/vulnerability/CVE-2021-47120
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

HID: magicmouse: fix NULL-deref on disconnect

Commit 9d7b18668956 ("HID: magicmouse: add support for Apple Magic
Trackpad 2") added a sanity check for an Apple trackpad but returned
success instead of -ENODEV when the check failed. This means that the
remove callback will dereference the never-initialised driver data
pointer when the driver is later unbound (e.g. on USB disconnect).

## References
- https://git.kernel.org/stable/c/368c5d45a87e1bcc7f1e98e0c255c37b7b12c5d6
- https://git.kernel.org/stable/c/4b4f6cecca446abcb686c6e6c451d4f1ec1a7497
- https://git.kernel.org/stable/c/9cf27473f21913a3eaf4702dd2a25415afd5f33f
- https://git.kernel.org/stable/c/b5d013c4c76b276890135b5d32803c4c63924b77
