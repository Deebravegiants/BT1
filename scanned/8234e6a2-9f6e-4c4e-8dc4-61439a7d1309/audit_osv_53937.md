# [H] CVE-2023-32784

## Summary
Severity: High
Advisory: CVE-2023-32784
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-05-15
Source: https://osv.dev/vulnerability/CVE-2023-32784
Type: osv

## Details
In KeePass 2.x before 2.54, it is possible to recover the cleartext master password from a memory dump, even when a workspace is locked or no longer running. The memory dump can be a KeePass process dump, swap file (pagefile.sys), hibernation file (hiberfil.sys), or RAM dump of the entire system. The first character cannot be recovered. In 2.54, there is different API usage and/or random string insertion for mitigation.

## References
- https://sourceforge.net/p/keepass/discussion/329220/thread/f3438e6283/
- https://github.com/keepassxreboot/keepassxc/discussions/9433
- https://github.com/vdohney/keepass-password-dumper
