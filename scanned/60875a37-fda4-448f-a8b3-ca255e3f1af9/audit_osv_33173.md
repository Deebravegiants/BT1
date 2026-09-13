# [H] audit: fix out-of-bounds read in audit_compare_dname_path()

## Summary
Severity: High
Advisory: CVE-2025-39840
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2025-09-19
Source: https://osv.dev/vulnerability/CVE-2025-39840
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.14.0 <6.16.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

audit: fix out-of-bounds read in audit_compare_dname_path()

When a watch on dir=/ is combined with an fsnotify event for a
single-character name directly under / (e.g., creating /a), an
out-of-bounds read can occur in audit_compare_dname_path().

The helper parent_len() returns 1 for "/". In audit_compare_dname_path(),
when parentlen equals the full path length (1), the code sets p = path + 1
and pathlen = 1 - 1 = 0. The subsequent loop then dereferences
p[pathlen - 1] (i.e., p[-1]), causing an out-of-bounds read.

Fix this by adding a pathlen > 0 check to the while loop condition
to prevent the out-of-bounds access.

[PM: subject tweak, sign-off email fixes]

## References
- https://git.kernel.org/stable/c/4540f1d23e7f387880ce46d11b5cd3f27248bf8d
- https://git.kernel.org/stable/c/9735a9dcc307427e7d6336c54171682f1bac9789
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39840.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39840
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
