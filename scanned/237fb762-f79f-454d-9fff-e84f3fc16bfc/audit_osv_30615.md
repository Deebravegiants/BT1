# [M] unicode: Fix utf8_load() error path

## Summary
Severity: Medium
Advisory: CVE-2024-53233
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-12-27
Source: https://osv.dev/vulnerability/CVE-2024-53233
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.17.0 <6.1.120, >=6.2.0 <6.6.64, >=6.7.0 <6.11.11, >=6.12.0 <6.12.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

unicode: Fix utf8_load() error path

utf8_load() requests the symbol "utf8_data_table" and then checks if the
requested UTF-8 version is supported. If it's unsupported, it tries to
put the data table using symbol_put(). If an unsupported version is
requested, symbol_put() fails like this:

 kernel BUG at kernel/module/main.c:786!
 RIP: 0010:__symbol_put+0x93/0xb0
 Call Trace:
  <TASK>
  ? __die_body.cold+0x19/0x27
  ? die+0x2e/0x50
  ? do_trap+0xca/0x110
  ? do_error_trap+0x65/0x80
  ? __symbol_put+0x93/0xb0
  ? exc_invalid_op+0x51/0x70
  ? __symbol_put+0x93/0xb0
  ? asm_exc_invalid_op+0x1a/0x20
  ? __pfx_cmp_name+0x10/0x10
  ? __symbol_put+0x93/0xb0
  ? __symbol_put+0x62/0xb0
  utf8_load+0xf8/0x150

That happens because symbol_put() expects the unique string that
identify the symbol, instead of a pointer to the loaded symbol. Fix that
by using such string.

## References
- https://git.kernel.org/stable/c/156bb2c569cd869583c593d27a5bd69e7b2a4264
- https://git.kernel.org/stable/c/4387cef540f36c2c9297460758cc2438305a24a0
- https://git.kernel.org/stable/c/6504dd27123966dc455494cb55217c04ca479121
- https://git.kernel.org/stable/c/89933f8ab3b4cad5ac14ea56a39947d1ffe7d0e3
- https://git.kernel.org/stable/c/c4b6c1781f6cc4e2283120ac8d873864b8056f21
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/53xxx/CVE-2024-53233.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-53233
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
