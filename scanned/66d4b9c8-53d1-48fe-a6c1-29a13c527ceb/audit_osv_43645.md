# [C] ksmbd: use memcmp() to compare ClientGUIDs

## Summary
Severity: Critical
Advisory: CVE-2026-74521
Ecosystem: Linux
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74521
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <7.1.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

ksmbd: use memcmp() to compare ClientGUIDs

ClientGUID is a fixed-size binary value and can contain embedded NUL
bytes. strncmp() stops comparing at the first NUL byte, so different
ClientGUID values can incorrectly be treated as equal.

Use memcmp() in SMB3 multichannel session binding and
FSCTL_VALIDATE_NEGOTIATE_INFO to compare all SMB2_CLIENT_GUID_SIZE
bytes.

## References
- https://git.kernel.org/stable/c/d535363299822c5caa543787b21bd5cfa3e41949
- https://git.kernel.org/stable/c/e8bb506e6ef749ac0336f3e579d8d02396b7d832
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74521.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74521
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
