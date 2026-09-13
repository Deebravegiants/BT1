# [H] md: fix double free of io_acct_set bioset

## Summary
Severity: High
Advisory: CVE-2022-49384
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49384
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.15.46, >=5.16.0 <5.17.14, >=5.17.0 <5.18.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

md: fix double free of io_acct_set bioset

Now io_acct_set is alloc and free in personality. Remove the codes that
free io_acct_set in md_free and md_stop.

## References
- https://git.kernel.org/stable/c/36a2fc44c574a59ee3b5e2cb327182f227b2b07e
- https://git.kernel.org/stable/c/42b805af102471f53e3c7867b8c2b502ea4eef7e
- https://git.kernel.org/stable/c/ea7d7bd90079d96f9c86bdaf0b106e0cd2a70661
- https://git.kernel.org/stable/c/f99d5b5dc8a42c807b5f1176b925aa45d61962ab
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49384.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49384
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
