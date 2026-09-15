# [H] CVE-2020-36785

## Summary
Severity: High
Advisory: CVE-2020-36785
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-02-28
Source: https://osv.dev/vulnerability/CVE-2020-36785
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

media: atomisp: Fix use after free in atomisp_alloc_css_stat_bufs()

The "s3a_buf" is freed along with all the other items on the
"asd->s3a_stats" list.  It leads to a double free and a use after free.

## References
- https://git.kernel.org/stable/c/801c1d505894008c888bc71d08d5cff5d87f8aba
- https://git.kernel.org/stable/c/8267ccd7b9df7ab682043507dd682fe0621cf045
- https://git.kernel.org/stable/c/ba11bbf303fafb33989e95473e409f6ab412b18d
- https://git.kernel.org/stable/c/d218c7a0284f6b92a7b82d2e19706e18663b4193
