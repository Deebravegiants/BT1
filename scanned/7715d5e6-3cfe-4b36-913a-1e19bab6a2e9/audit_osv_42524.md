# [H] wifi: at76c50x-usb: avoid length underflow in at76_guess_freq()

## Summary
Severity: High
Advisory: CVE-2026-68373
Ecosystem: Linux
CVSS: 8.1 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68373
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.30 <5.10.265, >=5.11.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.148, >=6.7.0 <6.12.101, >=6.13.0 <6.18.42, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: at76c50x-usb: avoid length underflow in at76_guess_freq()

at76_guess_freq() checks only that the received frame is at least a bare
802.11 header (24 bytes) before subtracting the fixed management-body
offset:

	len -= el_off;

For both beacon and probe response frames, el_off is 36. If the frame is
shorter than el_off, subtracting it causes the calculated IE length to
wrap. The length is eventually passed to cfg80211_find_elem_match() as a
very large unsigned value, so the element walk runs beyond the RX skb.

This path is reached from at76_rx_tasklet() while scanning. If the device
delivers a truncated beacon or probe response, the oversized IE length
causes an out-of-bounds read during scanning.

Skip the IE lookup if the frame does not reach the variable elements,
before subtracting el_off.

## References
- https://git.kernel.org/stable/c/4875680d1703f56afa6257ba30244f2fb44ed205
- https://git.kernel.org/stable/c/61a799ffd1e5a4fd3702d547828b7ff3d161468e
- https://git.kernel.org/stable/c/b406f33d234f98c8b310fdab5cbb492d85e98e49
- https://git.kernel.org/stable/c/bcde7249d45f52f994a9872bedf45994472ade77
- https://git.kernel.org/stable/c/cb831aff2f850f72bc5ff5ad77d0a70bb5a84061
- https://git.kernel.org/stable/c/e165a1d295e7e814e13b0f92c86e5d48309509ce
- https://git.kernel.org/stable/c/f742d9c98b5c504fc9e6744eef13a721c2aea486
- https://git.kernel.org/stable/c/fb1b50ab699211e777dca5ccfb648788b6a6e519
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68373.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68373
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
