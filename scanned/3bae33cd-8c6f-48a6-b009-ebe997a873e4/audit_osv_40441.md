# [H] Bluetooth: hci_sync: reject oversized Broadcast Announcement prepend

## Summary
Severity: High
Advisory: CVE-2026-53209
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-53209
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.1.176, >=6.2.0 <6.6.143, >=6.7.0 <6.12.94, >=6.13.0 <6.18.36, >=6.16.0 <7.0.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: hci_sync: reject oversized Broadcast Announcement prepend

Existing advertising instances can already hold the maximum extended
advertising payload. When hci_adv_bcast_annoucement() prepends the
Broadcast Announcement service data to that payload, the combined data
may no longer fit in the temporary buffer used to rebuild the
advertising data.

Reject that case before copying the existing payload and report the
failure through the device log. This keeps the existing advertising
data intact and avoids overrunning the temporary buffer.

## References
- https://git.kernel.org/stable/c/02f50e8bb69f9b22516163a09922f5537d3b12d1
- https://git.kernel.org/stable/c/10b0e832cc05d7aef4b92bed912cbd4a395d0862
- https://git.kernel.org/stable/c/1338ee049a8910ba6c9cee963920e978e6893c7d
- https://git.kernel.org/stable/c/5c65b96b549ea2dcfde497436bf9e048deb87758
- https://git.kernel.org/stable/c/cdd8bbdbee763fdf5bf343e6f7d4e79347739f62
- https://git.kernel.org/stable/c/dafc9f57140e66a10945127aa7433c3d715dc253
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53209.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53209
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
