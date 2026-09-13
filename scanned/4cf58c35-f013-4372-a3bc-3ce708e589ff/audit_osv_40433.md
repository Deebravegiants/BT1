# [M] USB: serial: io_ti: fix heap overflow in get_manuf_info()

## Summary
Severity: Medium
Advisory: CVE-2026-53196
Ecosystem: Linux
CVSS: 6.8 (CVSS:3.1/AV:P/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-53196
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <5.10.259, >=5.11.0 <5.15.210, >=5.16.0 <6.1.176, >=6.2.0 <6.6.143, >=6.7.0 <6.12.94, >=6.13.0 <6.18.36, >=6.19.0 <7.0.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

USB: serial: io_ti: fix heap overflow in get_manuf_info()

get_manuf_info() reads le16_to_cpu(rom_desc->Size) bytes from the
device I2C EEPROM into a buffer allocated with kmalloc_obj(), which
is sizeof(struct edge_ti_manuf_descriptor) = 10 bytes.

The Size field comes from the device and is only validated (in
check_i2c_image()) to make sure the descriptor fits within
TI_MAX_I2C_SIZE (16384 bytes), not against the destination buffer size.
A malicious USB device can therefore set Size to any value up to 16377,
causing a heap overflow of up to 16367 bytes when plugged into a host
running this driver.

valid_csum() is called after read_rom() and also iterates
buffer[0..Size-1], compounding the out-of-bounds access.

Fix by rejecting descriptors with unexpected length before calling
read_rom().

[ johan: amend commit message; also check for short descriptors ]

## References
- https://git.kernel.org/stable/c/183c1076eca43bbb3e7bdf597456f91d81c73e74
- https://git.kernel.org/stable/c/561edb021486e6723d841926aa4b48097da06190
- https://git.kernel.org/stable/c/b849f30d1a9e66aae6b715aaef66e427390cb081
- https://git.kernel.org/stable/c/cfd634f6dfd40c49a84f9bddc2867a80e2e2623a
- https://git.kernel.org/stable/c/d214d2341d4f9f447e36a7d012cdf6a6631a55f1
- https://git.kernel.org/stable/c/d92f17af7097d10bdeddf26f66f34b354104b277
- https://git.kernel.org/stable/c/e168db91442b94e64fa82a7dd297983d48ea5cc0
- https://git.kernel.org/stable/c/f96cf7bf9fbf15d7fcf0c91fec47ba8a010369ea
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-53196.json
- https://access.redhat.com/errata/RHSA-2026:61887
- https://access.redhat.com/errata/RHSA-2026:65708
- https://access.redhat.com/errata/RHSA-2026:65709
- https://access.redhat.com/errata/RHSA-2026:65710
- https://access.redhat.com/errata/RHSA-2026:65711
- https://access.redhat.com/errata/RHSA-2026:65712
- https://access.redhat.com/security/cve/CVE-2026-53196
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53196.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53196
- https://bugzilla.redhat.com/show_bug.cgi?id=2492750
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
