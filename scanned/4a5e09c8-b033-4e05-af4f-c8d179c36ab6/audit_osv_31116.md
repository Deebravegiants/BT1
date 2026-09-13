# [M] wifi: rtw89: chan: fix soft lockup in rtw89_entity_recalc_mgnt_roles()

## Summary
Severity: Medium
Advisory: CVE-2024-57991
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-27
Source: https://osv.dev/vulnerability/CVE-2024-57991
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.13.0 <6.13.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: rtw89: chan: fix soft lockup in rtw89_entity_recalc_mgnt_roles()

During rtw89_entity_recalc_mgnt_roles(), there is a normalizing process
which will re-order the list if an entry with target pattern is found.
And once one is found, should have aborted the list_for_each_entry. But,
`break` just aborted the inner for-loop. The outer list_for_each_entry
still continues. Normally, only the first entry will match the target
pattern, and the re-ordering will change nothing, so there won't be
soft lockup. However, in some special cases, soft lockup would happen.

Fix it by `goto fill` to break from the list_for_each_entry.

The following is a sample of kernel log for this problem.

watchdog: BUG: soft lockup - CPU#1 stuck for 26s! [wpa_supplicant:2055]
[...]
RIP: 0010:rtw89_entity_recalc ([...] chan.c:392 chan.c:479) rtw89_core
[...]

## References
- https://git.kernel.org/stable/c/01d2d34e9fcc9897081c3c16a666f793c8a38c58
- https://git.kernel.org/stable/c/223ba95fdcd3c6090e2bd51dce66abb6dd4f9df9
- https://git.kernel.org/stable/c/e4790b3e314a4814f1680a5dc552031fb199b878
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/57xxx/CVE-2024-57991.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-57991
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
