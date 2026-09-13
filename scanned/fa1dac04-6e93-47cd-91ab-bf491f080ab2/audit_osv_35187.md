# [C] ksmbd: fix use-after-free in ksmbd_tree_connect_put under concurrency

## Summary
Severity: Critical
Advisory: CVE-2025-68817
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-01-13
Source: https://osv.dev/vulnerability/CVE-2025-68817
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.15.199, >=5.16.0 <6.1.160, >=6.2.0 <6.6.120, >=6.6.0 <6.12.64, >=6.7.0 <6.18.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

ksmbd: fix use-after-free in ksmbd_tree_connect_put under concurrency

Under high concurrency, A tree-connection object (tcon) is freed on
a disconnect path while another path still holds a reference and later
executes *_put()/write on it.

## References
- https://git.kernel.org/stable/c/063cbbc6f595ea36ad146e1b7d2af820894beb21
- https://git.kernel.org/stable/c/21a3d01fc6db5129f81edb0ab7cb94fd758bcbea
- https://git.kernel.org/stable/c/446beed646b2e426dd53d27358365f8678e1dd01
- https://git.kernel.org/stable/c/b39a1833cc4a2755b02603eec3a71a85e9dff926
- https://git.kernel.org/stable/c/d092de8a26c952379ded8e6b0bda31d89befac1a
- https://git.kernel.org/stable/c/d64977495e44855f2b28d8ce56107c963a7a50e4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/68xxx/CVE-2025-68817.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-68817
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
