# [H] video: fbdev: s3fb: Check the size of screen before memset_io()

## Summary
Severity: High
Advisory: CVE-2022-50097
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H)
Published: 2025-06-18
Source: https://osv.dev/vulnerability/CVE-2022-50097
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.21 <4.14.291, >=4.15.0 <4.19.256, >=4.20.0 <5.4.211, >=5.5.0 <5.10.137, >=5.11.0 <5.15.61, >=5.16.0 <5.18.18, >=5.19.0 <5.19.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

video: fbdev: s3fb: Check the size of screen before memset_io()

In the function s3fb_set_par(), the value of 'screen_size' is
calculated by the user input. If the user provides the improper value,
the value of 'screen_size' may larger than 'info->screen_size', which
may cause the following bug:

[   54.083733] BUG: unable to handle page fault for address: ffffc90003000000
[   54.083742] #PF: supervisor write access in kernel mode
[   54.083744] #PF: error_code(0x0002) - not-present page
[   54.083760] RIP: 0010:memset_orig+0x33/0xb0
[   54.083782] Call Trace:
[   54.083788]  s3fb_set_par+0x1ec6/0x4040
[   54.083806]  fb_set_var+0x604/0xeb0
[   54.083836]  do_fb_ioctl+0x234/0x670

Fix the this by checking the value of 'screen_size' before memset_io().

## References
- https://git.kernel.org/stable/c/3c35a0dc2b4e7acf24c796043b64fa3eee799239
- https://git.kernel.org/stable/c/52461d387cc8c8f8dc40320caa2e9e101f73e7ba
- https://git.kernel.org/stable/c/574912261528589012b61f82d368256247c3a5a8
- https://git.kernel.org/stable/c/5e0da18956d38e7106664dc1d06367b22f06edd3
- https://git.kernel.org/stable/c/6ba592fa014f21f35a8ee8da4ca7b95a018f13e8
- https://git.kernel.org/stable/c/ce50d94afcb8690813c5522f24cd38737657db81
- https://git.kernel.org/stable/c/e2d7cacc6a2a1d77e7e20a492daf458a12cf19e0
- https://git.kernel.org/stable/c/eacb50f1733660911827d7c3720f4c5425d0cdda
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50097.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50097
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
