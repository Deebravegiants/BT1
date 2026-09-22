# [C] ksmbd: run set info with opener credentials

## Summary
Severity: Critical
Advisory: CVE-2026-64393
Ecosystem: Linux
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H)
Published: 2026-07-25
Source: https://osv.dev/vulnerability/CVE-2026-64393
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.96, >=6.13.0 <6.18.39, >=6.19.0 <7.1.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

ksmbd: run set info with opener credentials

SMB2 SET_INFO handlers call path-based VFS helpers after checking the
access mask granted to the SMB handle. Those helpers perform their owner,
inode permission and LSM checks using the current ksmbd worker credentials.

Run the complete SET_INFO dispatch with the credentials captured when the
handle was opened. This also removes the separate security information
credential setup and keeps all SET_INFO classes under one credential scope.

Direct override_creds() is used because it can nest with the request
credential overrides already used by rename and link helpers.

## References
- https://git.kernel.org/stable/c/0ce682867fd506f61f40c76bde7e4205bde34e87
- https://git.kernel.org/stable/c/20ee516a62989a8d505ee432f9e59525ea23984e
- https://git.kernel.org/stable/c/5cbabf3a71575cd31bc7785d92d4ab42338a654b
- https://git.kernel.org/stable/c/8cc9ec711f5255167247a9ab6a7179b787426ed7
- https://git.kernel.org/stable/c/b35afd5cf8fab236ef21117e42ee45691d4ffa7b
- https://git.kernel.org/stable/c/b383bcad3d2fe634b26efbce53e22bbb5753a520
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64393.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64393
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
