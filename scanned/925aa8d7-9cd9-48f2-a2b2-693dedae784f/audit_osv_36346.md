# [H] HID: i2c-hid: fix potential buffer overflow in i2c_hid_get_report()

## Summary
Severity: High
Advisory: CVE-2026-23178
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-02-14
Source: https://osv.dev/vulnerability/CVE-2026-23178
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.18.0 <6.1.163, >=6.2.0 <6.6.124, >=6.7.0 <6.12.70, >=6.13.0 <6.18.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

HID: i2c-hid: fix potential buffer overflow in i2c_hid_get_report()

`i2c_hid_xfer` is used to read `recv_len + sizeof(__le16)` bytes of data
into `ihid->rawbuf`.

The former can come from the userspace in the hidraw driver and is only
bounded by HID_MAX_BUFFER_SIZE(16384) by default (unless we also set
`max_buffer_size` field of `struct hid_ll_driver` which we do not).

The latter has size determined at runtime by the maximum size of
different report types you could receive on any particular device and
can be a much smaller value.

Fix this by truncating `recv_len` to `ihid->bufsize - sizeof(__le16)`.

The impact is low since access to hidraw devices requires root.

## References
- https://git.kernel.org/stable/c/2124279f1f8c32c1646ce98e75a1a39b23b7db76
- https://git.kernel.org/stable/c/2497ff38c530b1af0df5130ca9f5ab22c5e92f29
- https://git.kernel.org/stable/c/786ec171788bdf9dda38789163f1b1fbb47f2d1e
- https://git.kernel.org/stable/c/cff3f619fd1cb40cdd89971df9001f075613d219
- https://git.kernel.org/stable/c/f9c9ad89d845f88a1509e9d672f65d234425fde9
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23178.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-23178
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
