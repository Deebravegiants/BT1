# [H] usb: isp1760: Fix out-of-bounds array access

## Summary
Severity: High
Advisory: CVE-2022-49551
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49551
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.14.0 <5.15.46, >=5.16.0 <5.17.14, >=5.18.0 <5.18.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

usb: isp1760: Fix out-of-bounds array access

Running the driver through kasan gives an interesting splat:

  BUG: KASAN: global-out-of-bounds in isp1760_register+0x180/0x70c
  Read of size 20 at addr f1db2e64 by task swapper/0/1
  (...)
  isp1760_register from isp1760_plat_probe+0x1d8/0x220
  (...)

This happens because the loop reading the regmap fields for the
different ISP1760 variants look like this:

  for (i = 0; i < HC_FIELD_MAX; i++) { ... }

Meaning it expects the arrays to be at least HC_FIELD_MAX - 1 long.

However the arrays isp1760_hc_reg_fields[], isp1763_hc_reg_fields[],
isp1763_hc_volatile_ranges[] and isp1763_dc_volatile_ranges[] are
dynamically sized during compilation.

Fix this by putting an empty assignment to the [HC_FIELD_MAX]
and [DC_FIELD_MAX] array member at the end of each array.
This will make the array one member longer than it needs to be,
but avoids the risk of overwriting whatever is inside
[HC_FIELD_MAX - 1] and is simple and intuitive to read. Also
add comments explaining what is going on.

## References
- https://git.kernel.org/stable/c/26ae2c942b5702f2e43d36b2a4389cfb7d616b6a
- https://git.kernel.org/stable/c/463bddd3ff1acf4036ddb80c34a715eb99debf46
- https://git.kernel.org/stable/c/47d39cb57e8669e507d17d9e0d067d2b3e3a87ae
- https://git.kernel.org/stable/c/bf2558bbdce3ab1d6bcba09f354914e4515d0a2b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49551.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49551
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
