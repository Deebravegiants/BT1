# [M] wifi: rtw89: coex: check NULL return of kmalloc in btc_fw_set_monreg()

## Summary
Severity: Medium
Advisory: CVE-2024-56535
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-12-27
Source: https://osv.dev/vulnerability/CVE-2024-56535
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.10.0 <6.11.11, >=6.12.0 <6.12.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: rtw89: coex: check NULL return of kmalloc in btc_fw_set_monreg()

kmalloc may fail, return value might be NULL and will cause
NULL pointer dereference. Add check NULL return of kmalloc in
btc_fw_set_monreg().

## References
- https://git.kernel.org/stable/c/051577414271961f3f4c3bff87b427924b486219
- https://git.kernel.org/stable/c/64db1a42d98307001a48cec1b3e68ce9f905e73d
- https://git.kernel.org/stable/c/81df5ed446b448bdc327b7c7f0b50121fc1f4aa2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56535.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56535
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
