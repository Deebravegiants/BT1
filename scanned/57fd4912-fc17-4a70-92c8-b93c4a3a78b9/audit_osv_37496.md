# [H] ksmbd: validate owner of durable handle on reconnect

## Summary
Severity: High
Advisory: CVE-2026-31717
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-01
Source: https://osv.dev/vulnerability/CVE-2026-31717
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.6.142, >=6.7.0 <6.12.92, >=6.9.0 <6.18.25, >=6.13.0 <7.0.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

ksmbd: validate owner of durable handle on reconnect

Currently, ksmbd does not verify if the user attempting to reconnect
to a durable handle is the same user who originally opened the file.
This allows any authenticated user to hijack an orphaned durable handle
by predicting or brute-forcing the persistent ID.

According to MS-SMB2, the server MUST verify that the SecurityContext
of the reconnect request matches the SecurityContext associated with
the existing open.
Add a durable_owner structure to ksmbd_file to store the original opener's
UID, GID, and account name. and catpure the owner information when a file
handle becomes orphaned. and implementing ksmbd_vfs_compare_durable_owner()
to validate the identity of the requester during SMB2_CREATE (DHnC).

## References
- https://git.kernel.org/stable/c/00ce8d6789dae72d042a4522264964c72891ca37
- https://git.kernel.org/stable/c/49110a8ce654bbe56bef7c5e44cce31f4b102b8a
- https://git.kernel.org/stable/c/712cdf917e77a6444ce3836874829d770db20ee6
- https://git.kernel.org/stable/c/c7f0f0d01c88bdcb8b1694d7d321670013f7ed7d
- https://git.kernel.org/stable/c/c908c853f304a4969b5aa10eba0b50350cc65b80
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31717.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31717
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
