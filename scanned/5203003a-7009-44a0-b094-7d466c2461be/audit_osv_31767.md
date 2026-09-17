# [H] usbnet: ipheth: use static NDP16 location in URB

## Summary
Severity: High
Advisory: CVE-2025-21742
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2025-02-27
Source: https://osv.dev/vulnerability/CVE-2025-21742
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.5.0 <6.6.78, >=6.7.0 <6.12.14, >=6.13.0 <6.13.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

usbnet: ipheth: use static NDP16 location in URB

Original code allowed for the start of NDP16 to be anywhere within the
URB based on the `wNdpIndex` value in NTH16. Only the start position of
NDP16 was checked, so it was possible for even the fixed-length part
of NDP16 to extend past the end of URB, leading to an out-of-bounds
read.

On iOS devices, the NDP16 header always directly follows NTH16. Rely on
and check for this specific format.

This, along with NCM-specific minimal URB length check that already
exists, will ensure that the fixed-length part of NDP16 plus a set
amount of DPEs fit within the URB.

Note that this commit alone does not fully address the OoB read.
The limit on the amount of DPEs needs to be enforced separately.

## References
- https://git.kernel.org/stable/c/2b619445dcb6dab97d8ed033fb57225aca1288c4
- https://git.kernel.org/stable/c/86586dcb75cb8fd062a518aca8ee667938b91efb
- https://git.kernel.org/stable/c/8fb062178e1ce180e2cfdc9abc83a1b9fea381ca
- https://git.kernel.org/stable/c/cf1ac7f7cf601ac31d1580559c002b5e37b733b7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21742.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21742
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
