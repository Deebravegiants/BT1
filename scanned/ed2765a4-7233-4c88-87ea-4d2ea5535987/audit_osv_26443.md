# [H] rxrpc: Make it so that a waiting process can be aborted

## Summary
Severity: High
Advisory: CVE-2023-53218
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-15
Source: https://osv.dev/vulnerability/CVE-2023-53218
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.11.0 <6.2.16, >=6.3.0 <6.3.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

rxrpc: Make it so that a waiting process can be aborted

When sendmsg() creates an rxrpc call, it queues it to wait for a connection
and channel to be assigned and then waits before it can start shovelling
data as the encrypted DATA packet content includes a summary of the
connection parameters.

However, sendmsg() may get interrupted before a connection gets assigned
and further sendmsg() calls will fail with EBUSY until an assignment is
made.

Fix this so that the call can at least be aborted without failing on
EBUSY.  We have to be careful here as sendmsg() mustn't be allowed to start
the call timer if the call doesn't yet have a connection assigned as an
oops may follow shortly thereafter.

## References
- https://git.kernel.org/stable/c/0eb362d254814ce04848730bf32e75b8ee1a4d6c
- https://git.kernel.org/stable/c/7161cf61c64e9e9413d790f2fa2b9dada71a2249
- https://git.kernel.org/stable/c/876d96faacbc407daf4978d7ec95051b68f5344a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53218.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53218
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
