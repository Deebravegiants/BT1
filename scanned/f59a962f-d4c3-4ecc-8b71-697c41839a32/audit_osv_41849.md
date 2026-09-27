# [H] ethtool: eeprom: add more safeties to EEPROM Netlink fallback

## Summary
Severity: High
Advisory: CVE-2026-63985
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-63985
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.13.0 <5.15.210, >=5.16.0 <6.1.176, >=6.2.0 <6.6.143, >=6.7.0 <6.12.93, >=6.13.0 <6.18.35, >=6.19.0 <7.0.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

ethtool: eeprom: add more safeties to EEPROM Netlink fallback

The Netlink fallback path for reading module EEPROM
(fallback_set_params()) validates that offset < eeprom_len,
but does not check that offset + length stays within eeprom_len.
The ioctl equivalent (ethtool_get_any_eeprom() in ioctl.c) has
always enforced both bounds:

  if (eeprom.offset + eeprom.len > total_len)
      return -EINVAL;

This could lead to surprises in both drivers and device FW.
Add the missing offset + length validation to fallback_set_params(),
mirroring the ioctl.

Similarly - ethtool core in general, and ethtool_get_any_eeprom()
in particular tries to zero-init all buffers passed to the drivers
to avoid any extra work of zeroing things out. eeprom_fallback()
uses a plain kmalloc(), change it to zalloc.

## References
- https://git.kernel.org/stable/c/0e182689831277faf2ef683573a60474c208f690
- https://git.kernel.org/stable/c/4fe1bc4b3603f621240d5b401742f302190db769
- https://git.kernel.org/stable/c/65674d2489a12b8efd2ca0effb3de1d12224b596
- https://git.kernel.org/stable/c/67cfdd9210b99f260b3e0afeb9525e0acc7be31e
- https://git.kernel.org/stable/c/6ed7ebe22e9c3e3e946b6973c1ce43d3c38aeac1
- https://git.kernel.org/stable/c/d81376053a00865c70b8d8506a1cb93f2943d413
- https://git.kernel.org/stable/c/fd0de51c54fa8474a0ddeedd71c65ad09fada390
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63985.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-63985
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
