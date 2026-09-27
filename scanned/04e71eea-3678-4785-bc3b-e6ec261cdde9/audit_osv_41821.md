# [H] iio: buffer: hw-consumer: fix use-after-free in error path

## Summary
Severity: High
Advisory: CVE-2026-63930
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-63930
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.16.0 <5.10.259, >=5.11.0 <5.15.210, >=5.16.0 <6.1.176, >=6.2.0 <6.6.143, >=6.7.0 <6.12.93, >=6.13.0 <6.18.35, >=6.19.0 <7.0.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

iio: buffer: hw-consumer: fix use-after-free in error path

In the err_put_buffers cleanup path of iio_hw_consumer_alloc(), the code
was using list_for_each_entry() to iterate through buffers while calling
iio_buffer_put() which can free the current buffer if refcount drops to 0.
The list_for_each_entry() loop macro then evaluates buf->head.next to
continue iteration, accessing the freed buffer.

Fix this by using list_for_each_entry_safe().

## References
- https://git.kernel.org/stable/c/29783e6b6ec0b7152a15e53a063f17537e81177d
- https://git.kernel.org/stable/c/2ff615fc455acda5425c4900160cbe11cfea4449
- https://git.kernel.org/stable/c/6f5ed4f2c7c83f33344e0ba179f72a12e5dad4a4
- https://git.kernel.org/stable/c/9319c94f63ed10723afd738d79f5617daba87cc8
- https://git.kernel.org/stable/c/a3763ae33476328cf8d661742deb9daec78eac96
- https://git.kernel.org/stable/c/b71893c57730809c222766e5718bb33610f11963
- https://git.kernel.org/stable/c/d2759d49860b9a39b5cde2fb88e4b822ddf5f58f
- https://git.kernel.org/stable/c/e965627f0d442bfcae3f496c90cb653fb0917a61
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63930.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-63930
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
