# [H] smb: client: reject userspace cifs.spnego descriptions

## Summary
Severity: High
Advisory: CVE-2026-46243
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-06-01
Source: https://osv.dev/vulnerability/CVE-2026-46243
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.24 <5.10.258, >=5.11.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.142, >=6.7.0 <6.12.92, >=6.13.0 <6.18.34, >=6.19.0 <7.0.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

smb: client: reject userspace cifs.spnego descriptions

cifs.spnego key descriptions contain authority-bearing fields such as
pid, uid, creduid, and upcall_target that cifs.upcall treats as
kernel-originating inputs. However, userspace can also create keys of
this type through request_key(2) or add_key(2), allowing those fields to
be supplied without CIFS origin.

Only accept cifs.spnego descriptions while CIFS is using its private
spnego_cred to request the key.

## References
- http://www.openwall.com/lists/oss-security/2026/06/01/6
- https://git.kernel.org/stable/c/0aece6685fc80a8de492688ca2315fb86ec379c7
- https://git.kernel.org/stable/c/2035acfb17221729b1b8ac335e941868a04ca079
- https://git.kernel.org/stable/c/3da1fdf4efbc490041eb4f836bf596201203f8f2
- https://git.kernel.org/stable/c/7713bd320ed4fc3d08a227cd8e41242219a16981
- https://git.kernel.org/stable/c/91f89c1d83e80417629791fcef6af8140d7d01c8
- https://git.kernel.org/stable/c/9544559e59438a4b609b2fdfa0763d8360572824
- https://git.kernel.org/stable/c/a3bbda6502a9398b816fa2e71c9a3f955f58013d
- https://git.kernel.org/stable/c/cf20038657d6d4974349556a34e08fe0490bebbc
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-46243.json
- https://access.redhat.com/errata/RHSA-2026:23258
- https://access.redhat.com/errata/RHSA-2026:23259
- https://access.redhat.com/errata/RHSA-2026:23329
- https://access.redhat.com/errata/RHSA-2026:23395
- https://access.redhat.com/errata/RHSA-2026:24381
- https://access.redhat.com/errata/RHSA-2026:25908
- https://access.redhat.com/errata/RHSA-2026:26462
- https://access.redhat.com/errata/RHSA-2026:26515
- https://access.redhat.com/errata/RHSA-2026:26535
- https://access.redhat.com/errata/RHSA-2026:26563
