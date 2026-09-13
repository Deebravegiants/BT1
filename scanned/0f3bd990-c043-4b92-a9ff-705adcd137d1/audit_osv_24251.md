# [H] ipmi: fix use after free in _ipmi_destroy_user()

## Summary
Severity: High
Advisory: CVE-2022-50677
Ecosystem: Linux
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-09
Source: https://osv.dev/vulnerability/CVE-2022-50677
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <4.19.270, >=4.20.0 <5.4.229, >=5.5.0 <5.15.87, >=5.11.0 <6.0.18, >=5.16.0 <6.1.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

ipmi: fix use after free in _ipmi_destroy_user()

The intf_free() function frees the "intf" pointer so we cannot
dereference it again on the next line.

## References
- https://git.kernel.org/stable/c/1fc9b20a7688000fcf4d7fbaa58e415a3cdda961
- https://git.kernel.org/stable/c/35ad87bfe330f7ef6a19f772223c63296d643172
- https://git.kernel.org/stable/c/a92ce570c81dc0feaeb12a429b4bc65686d17967
- https://git.kernel.org/stable/c/bfce073089cb81482521c65061835aaa6d1a6cc0
- https://git.kernel.org/stable/c/d23006f2a56e11a3103de0ca8b843bf7fd7d76fc
- https://git.kernel.org/stable/c/f29d127b372e1b7662397d92341d9f7de198ff99
- https://git.kernel.org/stable/c/f7fde441198a9ecb130c3ccec91ee2131d6998ee
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50677.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50677
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
