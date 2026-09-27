# [H] bpf: Check bloom filter map value size

## Summary
Severity: High
Advisory: CVE-2024-36918
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-30
Source: https://osv.dev/vulnerability/CVE-2024-36918
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.16.0 <6.1.91, >=6.2.0 <6.6.31, >=6.7.0 <6.8.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

bpf: Check bloom filter map value size

This patch adds a missing check to bloom filter creating, rejecting
values above KMALLOC_MAX_SIZE. This brings the bloom map in line with
many other map types.

The lack of this protection can cause kernel crashes for value sizes
that overflow int's. Such a crash was caught by syzkaller. The next
patch adds more guard-rails at a lower level.

## References
- https://git.kernel.org/stable/c/608e13706c8b6c658a0646f09ebced74ec367f7c
- https://git.kernel.org/stable/c/a8d89feba7e54e691ca7c4efc2a6264fa83f3687
- https://git.kernel.org/stable/c/c418afb9bf23e2f2b76cb819601e4a5d9dbab42d
- https://git.kernel.org/stable/c/fa6995eeb62e74b5a1480c73fb7b420c270784d3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/36xxx/CVE-2024-36918.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-36918
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
