# [C] net: enetc: check the number of BDs needed for xdp_frame

## Summary
Severity: Critical
Advisory: CVE-2026-72399
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72399
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.13.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: enetc: check the number of BDs needed for xdp_frame

The size of xdp_redirect_arr array is ENETC_MAX_SKB_FRAGS. However, the
number of fragments contained in xdp_frame may be greater than or equal
to ENETC_MAX_SKB_FRAGS, which will cause the access to xdp_redirect_arr
to be out of bounds.

## References
- https://git.kernel.org/stable/c/1681cc7974a6123f5d5740b03bc11e4784bd2542
- https://git.kernel.org/stable/c/1ecb199b0e6d12ab6c26c0b7edf1a8f4472d9aed
- https://git.kernel.org/stable/c/555c5475e787802eeae0d2b91c2f66c330db2767
- https://git.kernel.org/stable/c/cfbc6e9b84dcc0aa2d65c84ea4745af327763209
- https://git.kernel.org/stable/c/d22829101ab675607ad6c3d420fb3ab875f46bbb
- https://git.kernel.org/stable/c/f55276160ffad3e235b657ee4b7304eb99b90e5c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72399.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72399
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
