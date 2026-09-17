# [C] CVE-2012-6712

## Summary
Severity: Critical
Advisory: CVE-2012-6712
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-07-27
Source: https://osv.dev/vulnerability/CVE-2012-6712
Type: osv

## Details
In the Linux kernel before 3.4, a buffer overflow occurs in drivers/net/wireless/iwlwifi/iwl-agn-sta.c, which will cause at least memory corruption.

## References
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=2da424b0773cea3db47e1e81db71eeebde8269d4
- https://github.com/torvalds/linux/commit/2da424b0773cea3db47e1e81db71eeebde8269d4
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=2da424b0773cea3db47e1e81db71eeebde8269d4
- https://github.com/torvalds/linux/commit/2da424b0773cea3db47e1e81db71eeebde8269d4
- https://mirrors.edge.kernel.org/pub/linux/kernel/v3.x/ChangeLog-3.4
