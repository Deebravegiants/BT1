# [H] crypto: essiv - Handle EBUSY correctly

## Summary
Severity: High
Advisory: CVE-2023-54046
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-24
Source: https://osv.dev/vulnerability/CVE-2023-54046
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.4.0 <5.4.235, >=5.5.0 <5.10.173, >=5.11.0 <5.15.99, >=5.16.0 <6.1.16, >=6.2.0 <6.2.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

crypto: essiv - Handle EBUSY correctly

As it is essiv only handles the special return value of EINPROGERSS,
which means that in all other cases it will free data related to the
request.

However, as the caller of essiv may specify MAY_BACKLOG, we also need
to expect EBUSY and treat it in the same way.  Otherwise backlogged
requests will trigger a use-after-free.

## References
- https://git.kernel.org/stable/c/69c67d451fc19d88e54f7d97e8e7c093e08357e1
- https://git.kernel.org/stable/c/796e02cca30a67322161f0745e5ce994bbe75605
- https://git.kernel.org/stable/c/840a1d3b77c1b062bd62b4733969a5b1efc274ce
- https://git.kernel.org/stable/c/a006aa3eedb8bfd6fe317c3cfe9c86ffe76b2385
- https://git.kernel.org/stable/c/b5a772adf45a32c68bef28e60621f12617161556
- https://git.kernel.org/stable/c/c61e7d182ee3f3f5ecf18a2964e303d49c539b52
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/54xxx/CVE-2023-54046.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-54046
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
