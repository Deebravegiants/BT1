# [H] ovl: keep err zero after successful ovl_cache_get()

## Summary
Severity: High
Advisory: CVE-2026-53174
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-53174
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.19.0 <7.0.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

ovl: keep err zero after successful ovl_cache_get()

ovl_iterate_merged() stores PTR_ERR(cache) in err before checking
IS_ERR(cache). On success err holds the truncated cache pointer and
can be returned as a bogus non-zero error.

The syzbot reproducer reaches this through overlay-on-overlay readdir:

  getdents64
    iterate_dir(outer overlay file)
      ovl_iterate_merged()
        ovl_cache_get()
          ovl_dir_read_merged()
            ovl_dir_read()
              iterate_dir(inner overlay file)
                ovl_iterate_merged()

Only compute PTR_ERR(cache) on the error path.

## References
- https://git.kernel.org/stable/c/1711b6ed6953cee5940ca4c3a6e77f1b3798cee2
- https://git.kernel.org/stable/c/e7051909a01bfb883bfa78b27514854068ac4b85
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53174.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53174
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
