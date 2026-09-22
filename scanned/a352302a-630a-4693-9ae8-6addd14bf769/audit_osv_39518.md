# [C] rxgk: Fix potential integer overflow in length check

## Summary
Severity: Critical
Advisory: CVE-2026-46039
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-27
Source: https://osv.dev/vulnerability/CVE-2026-46039
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.17.0 <6.18.27, >=6.19.0 <7.0.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

rxgk: Fix potential integer overflow in length check

Fix potential integer overflow in rxgk_extract_token() when checking the
length of the ticket.  Rather than rounding up the value to be tested
(which might overflow), round down the size of the available data.

## References
- https://git.kernel.org/stable/c/183d37f12d1c8ed24a5bfc7addad05510da22a94
- https://git.kernel.org/stable/c/43222ac484f93b3ec2d240a7575e1cedd31f5fa4
- https://git.kernel.org/stable/c/6929350080f4da292d111a3b33e53138fee51cec
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46039.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-46039
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
