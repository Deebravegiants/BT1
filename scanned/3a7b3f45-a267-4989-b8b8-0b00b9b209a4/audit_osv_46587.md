# [M] CVE-2014-0142

## Summary
Severity: Medium
Advisory: CVE-2014-0142
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-08-10
Source: https://osv.dev/vulnerability/CVE-2014-0142
Type: osv

## Details
QEMU, possibly before 2.0.0, allows local users to cause a denial of service (divide-by-zero error and crash) via a zero value in the (1) tracks field to the seek_to_sector function in block/parallels.c or (2) extent_size field in the bochs function in block/bochs.c.

## References
- http://rhn.redhat.com/errata/RHSA-2014-0420.html
- http://rhn.redhat.com/errata/RHSA-2014-0421.html
- http://www.debian.org/security/2014/dsa-3044
- https://bugzilla.redhat.com/show_bug.cgi?id=1078201
- https://bugzilla.redhat.com/show_bug.cgi?id=1078201
- http://git.qemu.org/?p=qemu.git%3Ba=commitdiff%3Bh=8e53abbc20d08ae3ec30c2054e1161314ad9501d
- http://git.qemu.org/?p=qemu.git%3Ba=commitdiff%3Bh=9302e863aa8baa5d932fc078967050c055fa1a7f
