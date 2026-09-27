# [H] ipmi: Rework user message limit handling

## Summary
Severity: High
Advisory: CVE-2025-40202
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-11-12
Source: https://osv.dev/vulnerability/CVE-2025-40202
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.19.0 <6.1.157, >=6.2.0 <6.6.113, >=6.7.0 <6.12.54, >=6.13.0 <6.17.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

ipmi: Rework user message limit handling

The limit on the number of user messages had a number of issues,
improper counting in some cases and a use after free.

Restructure how this is all done to handle more in the receive message
allocation routine, so all refcouting and user message limit counts
are done in that routine.  It's a lot cleaner and safer.

## References
- https://git.kernel.org/stable/c/0ed73be9a2547ffb9b5c1d879ad9bfab73d920b5
- https://git.kernel.org/stable/c/348121b29594d42d1635648fd3ed31dfa25351d5
- https://git.kernel.org/stable/c/53d6e403affbf6df2c859a0ea00ccfc1e72090ca
- https://git.kernel.org/stable/c/b52da4054ee0bf9ecb44996f2c83236ff50b3812
- https://git.kernel.org/stable/c/f63723ca7d7623f9dae1990973cd158671f03c56
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40202.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40202
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
