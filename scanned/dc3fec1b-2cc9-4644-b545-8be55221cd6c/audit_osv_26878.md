# [H] media: av7110: prevent underflow in write_ts_to_decoder()

## Summary
Severity: High
Advisory: CVE-2023-54284
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2025-12-30
Source: https://osv.dev/vulnerability/CVE-2023-54284
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.31 <4.14.315, >=4.15.0 <4.19.283, >=4.20.0 <5.4.243, >=5.5.0 <5.10.211, >=5.11.0 <5.15.111, >=5.16.0 <6.1.28, >=6.2.0 <6.2.15, >=6.3.0 <6.3.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

media: av7110: prevent underflow in write_ts_to_decoder()

The buf[4] value comes from the user via ts_play().  It is a value in
the u8 range.  The final length we pass to av7110_ipack_instant_repack()
is "len - (buf[4] + 1) - 4" so add a check to ensure that the length is
not negative.  It's not clear that passing a negative len value does
anything bad necessarily, but it's not best practice.

With the new bounds checking the "if (!len)" condition is no longer
possible or required so remove that.

## References
- https://git.kernel.org/stable/c/423350af9e27f005611bd881b1df2cab66de943d
- https://git.kernel.org/stable/c/620b983589e0223876bf1463b01100a9c67b56ba
- https://git.kernel.org/stable/c/6606e2404ee9e20a3ae5b42fc3660d41b739ed3e
- https://git.kernel.org/stable/c/6680af5be9f08d830567e9118f76d3e64684db8f
- https://git.kernel.org/stable/c/77eeb4732135c18c2fdfab80839645b393f3e774
- https://git.kernel.org/stable/c/7b93ab60fe9ed04be0ff155bc30ad39dea23e22b
- https://git.kernel.org/stable/c/86ba65e5357bfbb6c082f68b265a292ee1bdde1d
- https://git.kernel.org/stable/c/ca4ce92e3ec9fd3c7c936b912b95c53331d5159c
- https://git.kernel.org/stable/c/eed9496a0501357aa326ddd6b71408189ed872eb
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/54xxx/CVE-2023-54284.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-54284
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
