# [H] io_uring/waitid: always prune wait queue entry in io_waitid_wait()

## Summary
Severity: High
Advisory: CVE-2025-40047
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-28
Source: https://osv.dev/vulnerability/CVE-2025-40047
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.7.0 <6.12.53, >=6.13.0 <6.17.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

io_uring/waitid: always prune wait queue entry in io_waitid_wait()

For a successful return, always remove our entry from the wait queue
entry list. Previously this was skipped if a cancelation was in
progress, but this can race with another invocation of the wait queue
entry callback.

## References
- https://git.kernel.org/stable/c/2f8229d53d984c6a05b71ac9e9583d4354e3b91f
- https://git.kernel.org/stable/c/3e2205db2f0608898d535da1964e1b376aacfdaa
- https://git.kernel.org/stable/c/696ba6032081e617564a8113a001b8d7943cb928
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40047.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40047
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
