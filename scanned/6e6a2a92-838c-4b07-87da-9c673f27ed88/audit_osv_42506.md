# [H] accel: ethosu: Fix element size accounting for cmd stream validation

## Summary
Severity: High
Advisory: CVE-2026-68316
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68316
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

accel: ethosu: Fix element size accounting for cmd stream validation

There are 2 issues with the element size handling in the command stream
validation which result in too small of a size calculated when the
element size is 16/32/64 bits.

For NHWC format, the element size is simply missing from the
calculation.

The bitfield for the element size is different between IFM/IFM2 and
OFM. IFM and IFM2 encode the precision in parameter bits 2:3, while OFM
uses bits 1:2.

## References
- https://git.kernel.org/stable/c/18a551482a4a326790698b273e76d7575a51a57d
- https://git.kernel.org/stable/c/b4ae748f8e6cb65bb86e5a281bbb5b5e5f106527
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68316.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68316
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
