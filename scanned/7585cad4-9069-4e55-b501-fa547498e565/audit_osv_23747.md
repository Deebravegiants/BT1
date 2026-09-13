# [M] Input: sparcspkr - fix refcount leak in bbc_beep_probe

## Summary
Severity: Medium
Advisory: CVE-2022-49438
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49438
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.26 <4.9.318, >=4.10.0 <4.14.283, >=4.15.0 <4.19.247, >=4.20.0 <5.4.198, >=5.5.0 <5.10.121, >=5.11.0 <5.15.46, >=5.16.0 <5.17.14, >=5.18.0 <5.18.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

Input: sparcspkr - fix refcount leak in bbc_beep_probe

of_find_node_by_path() calls of_find_node_opts_by_path(),
which returns a node pointer with refcount
incremented, we should use of_node_put() on it when done.
Add missing of_node_put() to avoid refcount leak.

## References
- https://git.kernel.org/stable/c/1124e39fea0e2fdb4202f95b716cb97cc7de7cc7
- https://git.kernel.org/stable/c/2f51db16cb740ff90086189a1ef2581eab665591
- https://git.kernel.org/stable/c/353bc58ac6c782d4dcde9136a91d1f90867938fe
- https://git.kernel.org/stable/c/418b6a3e12f75638abc5673eb76cb32127d0ab13
- https://git.kernel.org/stable/c/6e07ccc7d56130f760d23f67a70c45366c07debc
- https://git.kernel.org/stable/c/73d6f42d8d86648bec2e73d34fe1648cb6d23e08
- https://git.kernel.org/stable/c/bbc2b0ce6042dd3117827f10ea8cb67e0ab786da
- https://git.kernel.org/stable/c/c8994b30d71d64d5dcc9bc0edbfdf367171aa96f
- https://git.kernel.org/stable/c/f13064b0f2c651a3fbb0749932795c6fd21556a8
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49438.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49438
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
