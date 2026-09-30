# [H] wifi: iwlwifi: mvm: set the cipher for secured NDP ranging

## Summary
Severity: High
Advisory: CVE-2024-49857
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H)
Published: 2024-10-21
Source: https://osv.dev/vulnerability/CVE-2024-49857
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.11.0 <6.11.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: iwlwifi: mvm: set the cipher for secured NDP ranging

The cipher pointer is not set, but is derefereced trying to set its
content, which leads to a NULL pointer dereference.
Fix it by pointing to the cipher parameter before dereferencing.

## References
- https://git.kernel.org/stable/c/a949075d4bbf1ca83ccdeaa6ef4ac2ce7526c5f4
- https://git.kernel.org/stable/c/b3322a6d6aa9bc17b395c4b38d3b97578887aa8a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/49xxx/CVE-2024-49857.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-49857
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
