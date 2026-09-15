# [H] of: Fix double free in of_parse_phandle_with_args_map

## Summary
Severity: High
Advisory: CVE-2023-52679
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-17
Source: https://osv.dev/vulnerability/CVE-2023-52679
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.17.0 <4.19.306, >=4.20.0 <5.4.268, >=5.5.0 <5.10.209, >=5.11.0 <5.15.148, >=5.16.0 <6.1.75, >=6.2.0 <6.6.14, >=6.7.0 <6.7.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

of: Fix double free in of_parse_phandle_with_args_map

In of_parse_phandle_with_args_map() the inner loop that
iterates through the map entries calls of_node_put(new)
to free the reference acquired by the previous iteration
of the inner loop. This assumes that the value of "new" is
NULL on the first iteration of the inner loop.

Make sure that this is true in all iterations of the outer
loop by setting "new" to NULL after its value is assigned to "cur".

Extend the unittest to detect the double free and add an additional
test case that actually triggers this path.

## References
- https://git.kernel.org/stable/c/26b4d702c44f9e5cf3c5c001ae619a4a001889db
- https://git.kernel.org/stable/c/4541004084527ce9e95a818ebbc4e6b293ffca21
- https://git.kernel.org/stable/c/4dde83569832f9377362e50f7748463340c5db6b
- https://git.kernel.org/stable/c/a0a061151a6200c13149dbcdb6c065203c8425d2
- https://git.kernel.org/stable/c/b64d09a4e8596f76d27f4b4a90a1cf6baf6a82f8
- https://git.kernel.org/stable/c/b9d760dae5b10e73369b769073525acd7b3be2bd
- https://git.kernel.org/stable/c/cafa992134124e785609a406da4ff2b54052aff7
- https://git.kernel.org/stable/c/d5f490343c77e6708b6c4aa7dbbfbcbb9546adea
- https://lists.debian.org/debian-lts-announce/2024/06/msg00016.html
- https://lists.debian.org/debian-lts-announce/2024/06/msg00020.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52679.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52679
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
