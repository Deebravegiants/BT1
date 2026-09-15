# [H] ksmbd: use list_first_entry_or_null for opinfo_get_list()

## Summary
Severity: High
Advisory: CVE-2025-38092
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-07-02
Source: https://osv.dev/vulnerability/CVE-2025-38092
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.6.88 <6.6.93, >=6.12.25 <6.12.32, >=6.14.4 <6.14.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

ksmbd: use list_first_entry_or_null for opinfo_get_list()

The list_first_entry() macro never returns NULL.  If the list is
empty then it returns an invalid pointer.  Use list_first_entry_or_null()
to check if the list is empty.

## References
- https://git.kernel.org/stable/c/10379171f346e6f61d30d9949500a8de4336444a
- https://git.kernel.org/stable/c/334da674b25fdb7a1a4d4b89dcd7795144fc7e11
- https://git.kernel.org/stable/c/c78abb646ff823e7d22faad4cc0703d4484da9e8
- https://git.kernel.org/stable/c/cb7e06e9736d73007dc8dab7b353733bb37df86b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38092.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38092
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
