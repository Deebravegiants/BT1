# [H] ksmbd: fix refcount leak causing resource not released

## Summary
Severity: High
Advisory: CVE-2025-39720
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-05
Source: https://osv.dev/vulnerability/CVE-2025-39720
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <6.6.103, >=6.7.0 <6.12.44, >=6.13.0 <6.16.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

ksmbd: fix refcount leak causing resource not released

When ksmbd_conn_releasing(opinfo->conn) returns true,the refcount was not
decremented properly, causing a refcount leak that prevents the count from
reaching zero and the memory from being released.

## References
- https://git.kernel.org/stable/c/36e010bb865fbaa1202fe9bcce3fd486d6db7606
- https://git.kernel.org/stable/c/89bb430f621124af39bb31763c4a8b504c9651e2
- https://git.kernel.org/stable/c/9a7abce6e8c0e2145b346a6d4abf0d9655e9b0e8
- https://git.kernel.org/stable/c/a1d2bab4d53368a526c97aba92671dd71814f95a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39720.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39720
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
