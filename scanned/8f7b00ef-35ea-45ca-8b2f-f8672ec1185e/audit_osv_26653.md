# [H] ext4: improve error handling from ext4_dirhash()

## Summary
Severity: High
Advisory: CVE-2023-53473
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-01
Source: https://osv.dev/vulnerability/CVE-2023-53473
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.2.0 <5.15.112, >=5.16.0 <6.1.29, >=6.2.0 <6.2.16, >=6.3.0 <6.3.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

ext4: improve error handling from ext4_dirhash()

The ext4_dirhash() will *almost* never fail, especially when the hash
tree feature was first introduced.  However, with the addition of
support of encrypted, casefolded file names, that function can most
certainly fail today.

So make sure the callers of ext4_dirhash() properly check for
failures, and reflect the errors back up to their callers.

## References
- https://git.kernel.org/stable/c/4b3cb1d108bfc2aebb0d7c8a52261a53cf7f5786
- https://git.kernel.org/stable/c/70d579aefa652a06af97e013e3fbbabbe5a43553
- https://git.kernel.org/stable/c/b2531936118deb3f479c4fa1bcd787b74b8faa6a
- https://git.kernel.org/stable/c/c1fae027da61fe8e7eb99f7244297e81bc0f1e43
- https://git.kernel.org/stable/c/f68876aeef96ef8b708ab10b9cb47ce0a5adb424
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53473.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53473
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
