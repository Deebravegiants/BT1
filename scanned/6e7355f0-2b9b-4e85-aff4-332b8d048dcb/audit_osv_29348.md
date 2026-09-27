# [H] bpf: Take return from set_memory_ro() into account with bpf_prog_lock_ro()

## Summary
Severity: High
Advisory: CVE-2024-42068
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-07-29
Source: https://osv.dev/vulnerability/CVE-2024-42068
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.18.0 <5.15.162, >=5.16.0 <6.1.97, >=6.2.0 <6.9.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

bpf: Take return from set_memory_ro() into account with bpf_prog_lock_ro()

set_memory_ro() can fail, leaving memory unprotected.

Check its return and take it into account as an error.

## References
- https://git.kernel.org/stable/c/05412471beba313ecded95aa17b25fe84bb2551a
- https://git.kernel.org/stable/c/7d2cc63eca0c993c99d18893214abf8f85d566d8
- https://git.kernel.org/stable/c/a359696856ca9409fb97655c5a8ef0f549cb6e03
- https://git.kernel.org/stable/c/e3540e5a7054d6daaf9a1415a48aacb092112a89
- https://git.kernel.org/stable/c/e4f602e3ff749ba770bf8ff10196e18358de6720
- https://git.kernel.org/stable/c/fdd411af8178edc6b7bf260f8fa4fba1bedd0a6d
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/42xxx/CVE-2024-42068.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-42068
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
