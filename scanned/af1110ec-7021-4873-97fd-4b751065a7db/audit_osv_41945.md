# [H] ksmbd: validate SID in parent security descriptor during ACL inheritance

## Summary
Severity: High
Advisory: CVE-2026-64138
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-64138
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <6.12.92, >=6.13.0 <6.18.34, >=6.19.0 <7.0.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

ksmbd: validate SID in parent security descriptor during ACL inheritance

Introduce smb_validate_ntsd_sid() helper to safely validate Owner SID
and Group SID inside the NT Security Descriptor (smb_ntsd) retrieved
from the parent directory.

## References
- https://git.kernel.org/stable/c/18d8db24b0a5b7be4829238dd4022236df02d421
- https://git.kernel.org/stable/c/1c9d0646a9959752f11ca1080dc1ff26bd1756cb
- https://git.kernel.org/stable/c/69f030cf95488ae1186c72ac8c66fd279664ea7f
- https://git.kernel.org/stable/c/f0e5c9c663badc9982e6941322eef1cb17de0f11
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64138.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64138
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
