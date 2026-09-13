# [C] s390/vfio_ccw: Limit the number of channel program segments

## Summary
Severity: Critical
Advisory: CVE-2026-80554
Ecosystem: Linux
CVSS: 9.3 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-08-26
Source: https://osv.dev/vulnerability/CVE-2026-80554
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.12.0 <6.6.153, >=6.7.0 <6.12.105, >=6.13.0 <6.18.46, >=6.19.0 <7.1.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

s390/vfio_ccw: Limit the number of channel program segments

The processing of channel programs, and the CCWs within them, is done
recursively. As such, there is an arbitrary (but not architectural)
limit to the number of CCWs that can exist in a single channel program.

The vfio-ccw logic breaks these channel programs into segments whenever
it encounters a Transfer-In-Channel (TIC) CCW, and the combined number
of segments count towards the global limit. Impose an equivalent limit
to the number of segments until such logic can be made non-recursive.

## References
- https://git.kernel.org/stable/c/06f4d6e5a8af6c2072e8cd39dbc512c683ca7fb2
- https://git.kernel.org/stable/c/15fb4559a7fdf0b8725e433a71cfd03a1313a48b
- https://git.kernel.org/stable/c/4ee94790490ae8dcc97df8597f07836c8a81bbcf
- https://git.kernel.org/stable/c/5405c90d6a47b3014e74ee0618a162449abbbc93
- https://git.kernel.org/stable/c/a1625f66eaa1200068a0e2c05bc90e65182fc4e3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80554.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80554
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
