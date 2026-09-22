# [M] io_uring: fix memory leak of uid in files registration

## Summary
Severity: Medium
Advisory: CVE-2022-49144
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49144
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.5.0 <5.10.110, >=5.11.0 <5.15.33, >=5.16.0 <5.16.19, >=5.17.0 <5.17.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

io_uring: fix memory leak of uid in files registration

When there are no files for __io_sqe_files_scm() to process in the
range, it'll free everything and return. However, it forgets to put uid.

## References
- https://git.kernel.org/stable/c/0853bd6885c2f293d88aaa7f7f1702c959b31680
- https://git.kernel.org/stable/c/7fa8b228c3f30060b9f4b24bb9aaaf41b0ae83fe
- https://git.kernel.org/stable/c/b27de7011cb3ba14b047be2cee0ed8278368665b
- https://git.kernel.org/stable/c/c86d18f4aa93e0e66cda0e55827cd03eea6bc5f8
- https://git.kernel.org/stable/c/d6d7a517e81accf6ed22d55684baea763d2dbe43
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49144.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49144
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
