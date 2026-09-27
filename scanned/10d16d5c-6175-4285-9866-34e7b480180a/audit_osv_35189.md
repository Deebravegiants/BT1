# [H] media: dvb-usb: dtv5100: fix out-of-bounds in dtv5100_i2c_msg()

## Summary
Severity: High
Advisory: CVE-2025-68819
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-01-13
Source: https://osv.dev/vulnerability/CVE-2025-68819
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.28 <5.10.248, >=5.11.0 <5.15.198, >=5.16.0 <6.1.160, >=6.2.0 <6.6.120, >=6.7.0 <6.12.64, >=6.13.0 <6.18.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

media: dvb-usb: dtv5100: fix out-of-bounds in dtv5100_i2c_msg()

rlen value is a user-controlled value, but dtv5100_i2c_msg() does not
check the size of the rlen value. Therefore, if it is set to a value
larger than sizeof(st->data), an out-of-bounds vuln occurs for st->data.

Therefore, we need to add proper range checking to prevent this vuln.

## References
- https://git.kernel.org/stable/c/4a54d8fcb093761e4c56eb211cf4e39bf8401fa1
- https://git.kernel.org/stable/c/61f214a878e96e2a8750bf96a98f78c658dba60c
- https://git.kernel.org/stable/c/ac92151ff2494130d9fc686055d6bbb9743a673e
- https://git.kernel.org/stable/c/b91e6aafe8d356086cc621bc03e35ba2299e4788
- https://git.kernel.org/stable/c/c2305b4c5fc15e20ac06c35738e0578eb4323750
- https://git.kernel.org/stable/c/c2c293ea7b61f12cdaad1e99a5b4efc58c88960a
- https://git.kernel.org/stable/c/fe3e129ab49806aaaa3f22067ebc75c2dfbe4658
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/68xxx/CVE-2025-68819.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-68819
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
