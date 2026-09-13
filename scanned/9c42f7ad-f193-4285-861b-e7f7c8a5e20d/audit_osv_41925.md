# [C] KVM: arm64: vgic-its: Reject restored DTE with out-of-range num_eventid_bits

## Summary
Severity: Critical
Advisory: CVE-2026-64106
Ecosystem: Linux
CVSS: 9.0 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-64106
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.12.0 <6.1.175, >=6.2.0 <6.6.142, >=6.7.0 <6.12.92, >=6.13.0 <6.18.34, >=6.19.0 <7.0.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

KVM: arm64: vgic-its: Reject restored DTE with out-of-range num_eventid_bits

Userspace can restore an ITS Device Table Entry whose Size field encodes
more EventID bits than the virtual ITS supports.  The live MAPD path
rejects that state, but vgic_its_restore_dte() accepts it and stores the
out-of-range value in dev->num_eventid_bits.

Reject restored DTEs with num_eventid_bits > VITS_TYPER_IDBITS before
allocating the device.  This mirrors the MAPD check and prevents the
restored state from reaching vgic_its_restore_itt(), where the unchecked
value can be converted into an oversized scan_its_table() range.

## References
- https://git.kernel.org/stable/c/0680f511926589206f81f57f76ce131d7741a316
- https://git.kernel.org/stable/c/1716b7fea2ead941a0dfac06c4504a3437cdf00d
- https://git.kernel.org/stable/c/8bcd15b690a390241179516af1b6ae49ebfd9d95
- https://git.kernel.org/stable/c/9ce754ed8e7ab4e3999767ce1505f85c449ccb07
- https://git.kernel.org/stable/c/b94538186a3eae3763b8f96dacd610920a865aa7
- https://git.kernel.org/stable/c/dab9f93251b2c86a033de6098d0c73afddd55d4a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64106.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64106
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
