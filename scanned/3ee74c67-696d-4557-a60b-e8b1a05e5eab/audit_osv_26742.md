# [H] HID: hidraw: fix data race on device refcount

## Summary
Severity: High
Advisory: CVE-2023-53759
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-08
Source: https://osv.dev/vulnerability/CVE-2023-53759
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.17.0 <6.1.37, >=6.2.0 <6.3.11, >=6.4.0 <6.4.1

## Details
In the Linux kernel, the following vulnerability has been resolved:

HID: hidraw: fix data race on device refcount

The hidraw_open() function increments the hidraw device reference
counter. The counter has no dedicated synchronization mechanism,
resulting in a potential data race when concurrently opening a device.

The race is a regression introduced by commit 8590222e4b02 ("HID:
hidraw: Replace hidraw device table mutex with a rwsem"). While
minors_rwsem is intended to protect the hidraw_table itself, by instead
acquiring the lock for writing, the reference counter is also protected.
This is symmetrical to hidraw_release().

## References
- https://git.kernel.org/stable/c/05b47034e2488c2924e5c032e20a1979d012b5b5
- https://git.kernel.org/stable/c/879e79c3aead41b8aa2e91164354b30bd1c4ef3b
- https://git.kernel.org/stable/c/944ee77dc6ec7b0afd8ec70ffc418b238c92f12b
- https://git.kernel.org/stable/c/ff348eabd97577da974d3db7038857f28c61d2bd
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53759.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53759
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
