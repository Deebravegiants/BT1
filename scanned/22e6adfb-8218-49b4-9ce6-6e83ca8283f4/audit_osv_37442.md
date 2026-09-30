# [H] ksmbd: require 3 sub-authorities before reading sub_auth[2]

## Summary
Severity: High
Advisory: CVE-2026-31611
Ecosystem: Linux
CVSS: 8.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:H)
Published: 2026-04-24
Source: https://osv.dev/vulnerability/CVE-2026-31611
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <6.1.175, >=6.2.0 <6.6.136, >=6.7.0 <6.12.83, >=6.13.0 <6.18.24, >=6.19.0 <6.19.14, >=6.20.0 <7.0.1

## Details
In the Linux kernel, the following vulnerability has been resolved:

ksmbd: require 3 sub-authorities before reading sub_auth[2]

parse_dacl() compares each ACE SID against sid_unix_NFS_mode and on
match reads sid.sub_auth[2] as the file mode.  If sid_unix_NFS_mode is
the prefix S-1-5-88-3 with num_subauth = 2 then compare_sids() compares
only min(num_subauth, 2) sub-authorities so a client SID with
num_subauth = 2 and sub_auth = {88, 3} will match.

If num_subauth = 2 and the ACE is placed at the very end of the security
descriptor, sub_auth[2] will be  4 bytes past end_of_acl.  The
out-of-band bytes will then be masked to the low 9 bits and applied as
the file's POSIX mode, probably not something that is good to have
happen.

Fix this up by forcing the SID to actually carry a third sub-authority
before reading it at all.

## References
- https://git.kernel.org/stable/c/08f9e6d899b5c834bbcc239eae1bed58d9b15d2c
- https://git.kernel.org/stable/c/46bbcd3ebfb3549c8da1838fc4493e79bd3241e7
- https://git.kernel.org/stable/c/53370cf9090777774e07fd9a8ebce67c6cc333ab
- https://git.kernel.org/stable/c/9401f86a224f37b50e6a3ccf1d46a70d5ef8af0a
- https://git.kernel.org/stable/c/b5b5d5936a50497fb151c0b122899a6894721c2b
- https://git.kernel.org/stable/c/cf2148b880fb7c0fcd727202dbc4fd5d6998b9c2
- https://git.kernel.org/stable/c/d2454f4a002d08560a60f214f392e6491cf11560
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31611.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31611
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
