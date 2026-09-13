# [H] tracing/user_events: Ensure write index cannot be negative

## Summary
Severity: High
Advisory: CVE-2023-54139
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-24
Source: https://osv.dev/vulnerability/CVE-2023-54139
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.18.0 <6.1.28, >=6.2.0 <6.2.15, >=6.3.0 <6.3.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

tracing/user_events: Ensure write index cannot be negative

The write index indicates which event the data is for and accesses a
per-file array. The index is passed by user processes during write()
calls as the first 4 bytes. Ensure that it cannot be negative by
returning -EINVAL to prevent out of bounds accesses.

Update ftrace self-test to ensure this occurs properly.

## References
- https://git.kernel.org/stable/c/0489c2b2c3104b89f078dbcec8c744dfc157d3e9
- https://git.kernel.org/stable/c/4fe46b5adf18e3dc606e62c9e6a0413398a17572
- https://git.kernel.org/stable/c/cd98c93286a30cc4588dfd02453bec63c2f4acf4
- https://git.kernel.org/stable/c/fa7f2f5d1739452280c22727c4384a52b72ab5de
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/54xxx/CVE-2023-54139.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-54139
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
