# [H] keys: Fix UAF in key_put()

## Summary
Severity: High
Advisory: CVE-2025-21893
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-03-31
Source: https://osv.dev/vulnerability/CVE-2025-21893
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.10.0 <6.12.21, >=6.13.0 <6.13.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

keys: Fix UAF in key_put()

Once a key's reference count has been reduced to 0, the garbage collector
thread may destroy it at any time and so key_put() is not allowed to touch
the key after that point.  The most key_put() is normally allowed to do is
to touch key_gc_work as that's a static global variable.

However, in an effort to speed up the reclamation of quota, this is now
done in key_put() once the key's usage is reduced to 0 - but now the code
is looking at the key after the deadline, which is forbidden.

Fix this by using a flag to indicate that a key can be gc'd now rather than
looking at the key's refcount in the garbage collector.

## References
- https://git.kernel.org/stable/c/6afe2ea2daec156bd94ad2c5a6f4f4c48240dcd3
- https://git.kernel.org/stable/c/75845c6c1a64483e9985302793dbf0dfa5f71e32
- https://git.kernel.org/stable/c/f6a3cf833188e897c97028cd7b926e3f2cb1a8c0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21893.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21893
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
