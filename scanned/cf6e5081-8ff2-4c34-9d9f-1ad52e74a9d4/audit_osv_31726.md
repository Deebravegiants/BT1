# [H] vfio/platform: check the bounds of read/write syscalls

## Summary
Severity: High
Advisory: CVE-2025-21687
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-10
Source: https://osv.dev/vulnerability/CVE-2025-21687
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.1.0 <5.4.290, >=5.5.0 <5.10.234, >=5.11.0 <5.15.178, >=5.16.0 <6.1.128, >=6.2.0 <6.6.75, >=6.7.0 <6.12.12, >=6.13.0 <6.13.1

## Details
In the Linux kernel, the following vulnerability has been resolved:

vfio/platform: check the bounds of read/write syscalls

count and offset are passed from user space and not checked, only
offset is capped to 40 bits, which can be used to read/write out of
bounds of the device.

## References
- https://git.kernel.org/stable/c/1485932496a1b025235af8aa1e21988d6b7ccd54
- https://git.kernel.org/stable/c/665cfd1083866f87301bbd232cb8ba48dcf4acce
- https://git.kernel.org/stable/c/6bcb8a5b70b80143db9bf12dfa7d53636f824d53
- https://git.kernel.org/stable/c/92340e6c5122d823ad064984ef7513eba9204048
- https://git.kernel.org/stable/c/9377cdc118cf327248f1a9dde7b87de067681dc9
- https://git.kernel.org/stable/c/a20fcaa230f7472456d12cf761ed13938e320ac3
- https://git.kernel.org/stable/c/c981c32c38af80737a2fedc16e270546d139ccdd
- https://git.kernel.org/stable/c/ce9ff21ea89d191e477a02ad7eabf4f996b80a69
- https://git.kernel.org/stable/c/d19a8650fd3d7aed8d1af1d9a77f979a8430eba1
- https://git.kernel.org/stable/c/ed81d82bb6e9df3a137f2c343ed689e6c68268ef
- https://git.kernel.org/stable/c/f21636f24b6786c8b13f1af4319fa75ffcf17f38
- https://git.kernel.org/stable/c/f65ce06387f8c1fb54bd59e18a8428248ec68eaf
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21687.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21687
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
