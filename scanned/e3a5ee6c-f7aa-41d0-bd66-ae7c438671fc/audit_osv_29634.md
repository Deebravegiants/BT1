# [H] s390/dasd: fix error recovery leading to data corruption on ESE devices

## Summary
Severity: High
Advisory: CVE-2024-45026
Ecosystem: Linux
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-09-11
Source: https://osv.dev/vulnerability/CVE-2024-45026
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.3.0 <5.4.283, >=5.5.0 <5.10.225, >=5.11.0 <5.15.166, >=5.16.0 <6.1.107, >=6.2.0 <6.6.48, >=6.7.0 <6.10.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

s390/dasd: fix error recovery leading to data corruption on ESE devices

Extent Space Efficient (ESE) or thin provisioned volumes need to be
formatted on demand during usual IO processing.

The dasd_ese_needs_format function checks for error codes that signal
the non existence of a proper track format.

The check for incorrect length is to imprecise since other error cases
leading to transport of insufficient data also have this flag set.
This might lead to data corruption in certain error cases for example
during a storage server warmstart.

Fix by removing the check for incorrect length and replacing by
explicitly checking for invalid track format in transport mode.

Also remove the check for file protected since this is not a valid
ESE handling case.

## References
- https://git.kernel.org/stable/c/0a228896a1b3654cd461ff654f6a64e97a9c3246
- https://git.kernel.org/stable/c/19f60a55b2fda49bc4f6134a5f6356ef62ee69d8
- https://git.kernel.org/stable/c/5d4a304338daf83ace2887aaacafd66fe99ed5cc
- https://git.kernel.org/stable/c/7db4042336580dfd75cb5faa82c12cd51098c90b
- https://git.kernel.org/stable/c/93a7e2856951680cd7fe6ebd705ac10c8a8a5efd
- https://git.kernel.org/stable/c/a665e3b7ac7d5cdc26e00e3d0fc8fd490e00316a
- https://git.kernel.org/stable/c/e245a18281c252c8dbc467492e09bb5d4b012118
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/45xxx/CVE-2024-45026.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-45026
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
