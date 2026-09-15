# [H] netfilter: xt_hashlimit: validate hashtable supports XT_HASHLIMIT_RATE_MATCH

## Summary
Severity: High
Advisory: CVE-2026-74564
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74564
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.14.0 <5.10.265, >=5.11.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.151, >=6.7.0 <6.12.103, >=6.13.0 <6.18.44, >=6.19.0 <7.1.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: xt_hashlimit: validate hashtable supports XT_HASHLIMIT_RATE_MATCH

The XT_HASHLIMIT_RATE_MATCH flag mode changes the semantics of the
dsthash_ent structure which represents an entry in the hashtable.  There
is a union area which uses a different layout to express the rate match
mode.

Update .checkentry path to validate the XT_HASHLIMIT_RATE_MATCH mode
flag is requested by two or more different rules that refer to the same
hashtable. Otherwise, uninitialized access to the burst field in the
union is possible.

Reject the use of the XT_HASHLIMIT_RATE_MATCH mode flag if set on by
revision less than 3 too.

## References
- https://git.kernel.org/stable/c/06a76334243ccd875a981aa8bb46c0f931ef1e3b
- https://git.kernel.org/stable/c/24683fea1f06bd3bd2707b99460e859bc6464c22
- https://git.kernel.org/stable/c/305b63e1402267459fdabb183af4527f6799eebf
- https://git.kernel.org/stable/c/32ec8d4aba2cf22e12bdc28df8c4bd833c195fc0
- https://git.kernel.org/stable/c/402befce5854c195058cf4bab7c78ca286068a26
- https://git.kernel.org/stable/c/d186f77d18bdfb252d401ff992ca3001a6a65a0f
- https://git.kernel.org/stable/c/dee686b5e7f21180538ff719867702f411c8eb5c
- https://git.kernel.org/stable/c/f76ab783e7d8d33e33dd7dfa697297f70d57b0e8
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74564.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74564
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
