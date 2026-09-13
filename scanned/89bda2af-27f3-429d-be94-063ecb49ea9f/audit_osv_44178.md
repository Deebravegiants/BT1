# [H] s390/vfio_ccw: Fix out of bounds check on CCW array

## Summary
Severity: High
Advisory: CVE-2026-80550
Ecosystem: Linux
CVSS: 7.9 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:L)
Published: 2026-08-26
Source: https://osv.dev/vulnerability/CVE-2026-80550
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.12.0 <5.10.266, >=5.11.0 <5.15.217, >=5.16.0 <6.1.184, >=6.2.0 <6.6.153, >=6.7.0 <6.12.105, >=6.13.0 <6.18.46, >=6.19.0 <7.1.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

s390/vfio_ccw: Fix out of bounds check on CCW array

The routine ccwchain_calc_length() counts the number of channel
command words (CCWs) that are chained together in a single channel
program, and rejects anything larger than CCWCHAIN_LEN_MAX (256) CCWs.

The loop itself is "do..while (count < 257)", and while the logic in
is_cpa_within_range() correctly adjusts between the 0-index array of
CCWs and the count of CCWs starting at 1, this means it would look
at a possible 257th CCW before ending the loop and (correctly)
returning an error.

Fix this by restructuring the loop to break as soon as 256 CCWs
(thus indexes 0-255) are examined, without looking at memory
outside the range.

## References
- https://git.kernel.org/stable/c/0282fb1c4b638eecfe2cc558092c460911d8f7e2
- https://git.kernel.org/stable/c/499a8a66b1598bfab97182aed15e0f1646074a3d
- https://git.kernel.org/stable/c/4c2e1d359d7a2b82cdf3254e4e480af9417f99fb
- https://git.kernel.org/stable/c/907adc667d902fafbdb2d740d57b55bd025dc4cd
- https://git.kernel.org/stable/c/a005b7f1a491ffda61bff0fd0f6548f8986fb977
- https://git.kernel.org/stable/c/af3f80ca4c8b17f20f9e588def076288fdb49e65
- https://git.kernel.org/stable/c/d5d096cd9369e986d4e5153baa86b8b35c283e09
- https://git.kernel.org/stable/c/f20be33d093ce7630c17ff7ed93caf7eaf8ac1a3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80550.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80550
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
