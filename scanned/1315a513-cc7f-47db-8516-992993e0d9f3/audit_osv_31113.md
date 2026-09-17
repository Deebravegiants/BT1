# [M] Bluetooth: btbcm: Fix NULL deref in btbcm_get_board_name()

## Summary
Severity: Medium
Advisory: CVE-2024-57988
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-27
Source: https://osv.dev/vulnerability/CVE-2024-57988
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.9.0 <6.12.13, >=6.13.0 <6.13.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: btbcm: Fix NULL deref in btbcm_get_board_name()

devm_kstrdup() can return a NULL pointer on failure,but this
returned value in btbcm_get_board_name() is not checked.
Add NULL check in btbcm_get_board_name(), to handle kernel NULL
pointer dereference error.

## References
- https://git.kernel.org/stable/c/74af8b9d0e79deefd2d43e14b84575839a849169
- https://git.kernel.org/stable/c/b88655bc6593c6a7fdc1248b212d17e581c4334e
- https://git.kernel.org/stable/c/df2f2d9199e61819cca5da0121dfa4d4cb57000f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/57xxx/CVE-2024-57988.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-57988
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
