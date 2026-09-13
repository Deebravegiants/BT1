# [H] md/raid10: check slab-out-of-bounds in md_bitmap_get_counter

## Summary
Severity: High
Advisory: CVE-2023-53357
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2025-09-17
Source: https://osv.dev/vulnerability/CVE-2023-53357
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.36 <4.19.291, >=4.20.0 <5.4.251, >=5.5.0 <5.10.188, >=5.11.0 <5.15.121, >=5.16.0 <6.1.39, >=6.2.0 <6.3.13, >=6.4.0 <6.4.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

md/raid10: check slab-out-of-bounds in md_bitmap_get_counter

If we write a large number to md/bitmap_set_bits, md_bitmap_checkpage()
will return -EINVAL because 'page >= bitmap->pages', but the return value
was not checked immediately in md_bitmap_get_counter() in order to set
*blocks value and slab-out-of-bounds occurs.

Move check of 'page >= bitmap->pages' to md_bitmap_get_counter() and
return directly if true.

## References
- https://git.kernel.org/stable/c/152bb26796ff054af50b2ee1b3ca56e364e4f61b
- https://git.kernel.org/stable/c/301867b1c16805aebbc306aafa6ecdc68b73c7e5
- https://git.kernel.org/stable/c/374fb914304d9b500721007f3837ea8f1f9a2418
- https://git.kernel.org/stable/c/39fa14e824acfd470db4f42c354297456bd82b53
- https://git.kernel.org/stable/c/a134dd582c0d5b6068efa308bd485cf1d00b3f65
- https://git.kernel.org/stable/c/b0b971fe7d61411ede63c3291764dbde1577ef2c
- https://git.kernel.org/stable/c/be1a3ec63a840cc9e59a033acf154f56255699a1
- https://git.kernel.org/stable/c/bea301c046110bf421a3ce153fb868cb8d618e90
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53357.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53357
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
