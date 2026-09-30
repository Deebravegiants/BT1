# [M] md/raid10: fix leak of 'r10bio->remaining' for recovery

## Summary
Severity: Medium
Advisory: CVE-2023-53299
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-16
Source: https://osv.dev/vulnerability/CVE-2023-53299
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.3.0 <4.14.315, >=4.15.0 <4.19.283, >=4.20.0 <5.4.243, >=5.5.0 <5.10.180, >=5.11.0 <5.15.111, >=5.16.0 <6.1.28, >=6.2.0 <6.2.15, >=6.3.0 <6.3.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

md/raid10: fix leak of 'r10bio->remaining' for recovery

raid10_sync_request() will add 'r10bio->remaining' for both rdev and
replacement rdev. However, if the read io fails, recovery_request_write()
returns without issuing the write io, in this case, end_sync_request()
is only called once and 'remaining' is leaked, cause an io hang.

Fix the problem by decreasing 'remaining' according to if 'bio' and
'repl_bio' is valid.

## References
- https://git.kernel.org/stable/c/11141630f03efffdfe260b3582b2d93d38171b97
- https://git.kernel.org/stable/c/1697fb124c6d6c5237e9cbd78890310154738084
- https://git.kernel.org/stable/c/1d2c6c6e37fe5de11fd01a82badf03390e12df7a
- https://git.kernel.org/stable/c/26208a7cffd0c7cbf14237ccd20c7270b3ffeb7e
- https://git.kernel.org/stable/c/3481dec5ecbbbbe44ab23e22c2b14bd65c644ec6
- https://git.kernel.org/stable/c/4f82e7e07cdaf2947d71968e3d6b73370a217093
- https://git.kernel.org/stable/c/8c5d5d7ffd1e76734811b8ea5417cf0432b9952c
- https://git.kernel.org/stable/c/8d09065802c53cc938d162b62f6c4150b392c90e
- https://git.kernel.org/stable/c/cb827ed2bb34480dc102146d3a1f89fdbcafc028
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53299.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53299
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
