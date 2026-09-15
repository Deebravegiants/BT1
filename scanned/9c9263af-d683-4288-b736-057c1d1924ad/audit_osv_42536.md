# [C] smb/client: handle overlapping allocated ranges in fallocate

## Summary
Severity: Critical
Advisory: CVE-2026-68388
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68388
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.10.265, >=5.11.0 <5.15.216, >=5.14.0 <6.1.183, >=5.16.0 <6.6.148, >=6.2.0 <6.12.101, >=6.7.0 <6.18.42, >=6.13.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

smb/client: handle overlapping allocated ranges in fallocate

smb3_simple_fallocate_range() can skip holes when an allocated range
returned by the server starts before the current fallocate offset. The
skipped hole is not zero-filled, but fallocate still returns success. A
later write to that hole may therefore fail with ENOSPC.

The function queries allocated ranges so that it can preserve existing
contents and write zeroes only into holes. However, the server may return
a range that starts before the current fallocate offset.

For example, assume the fallocate request is [100, 400) and the only
allocated range returned by the server is [0, 200):

        Request:      [100, 400)
        Server range: [  0, 200)  allocated

        Correct:
        [100, 200)    allocated data, skip
        [200, 400)    hole, zero-fill

        Current:
        [100, 300)    skipped
        [300, 400)    zero-filled afterwards

The current code adds the full server range length, 200, to the current
offset 100 and moves to 300. As a result, the hole in [200, 300) is
skipped without being zero-filled.

Fix this by advancing only over the part of the allocated range that
overlaps the current fallocate offset.  Ignore ranges that end before the
current offset and reject ranges whose end offset overflows.

This also prevents a malformed range length from causing an out-of-bounds
zero-buffer read.

## References
- https://git.kernel.org/stable/c/01719883235507b1585e4c51e320d9a7113dc698
- https://git.kernel.org/stable/c/377fe3e583e46369ee1004d5cfe12271d6589a68
- https://git.kernel.org/stable/c/437637f5ff3f573b2edf8571de91fb00a21eb4e6
- https://git.kernel.org/stable/c/7e08ab7a061b17ac1989a225c6afb53f44a86808
- https://git.kernel.org/stable/c/a4a09e5142835633fffbde68bd0a039ba4d4bf97
- https://git.kernel.org/stable/c/aeb58a4eb39a7ff4d7782b4f4ada0fda5e0675d2
- https://git.kernel.org/stable/c/b09ae45d85dc816987a71db9eebc54b0ae288e94
- https://git.kernel.org/stable/c/f47c7277c03a636fcc3a57969f2dc09567b3c050
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68388.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68388
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
