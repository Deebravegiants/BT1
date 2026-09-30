# [M] CVE-2017-17381

## Summary
Severity: Medium
Advisory: CVE-2017-17381
CVSS: 6.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2017-12-07
Source: https://osv.dev/vulnerability/CVE-2017-17381
Type: osv

## Details
The Virtio Vring implementation in QEMU allows local OS guest users to cause a denial of service (divide-by-zero error and QEMU process crash) by unsetting vring alignment while updating Virtio rings.

## References
- http://www.openwall.com/lists/oss-security/2017/12/05/2
- http://www.securityfocus.com/bid/102059
- https://usn.ubuntu.com/3575-1/
- https://www.debian.org/security/2018/dsa-4213
- https://lists.gnu.org/archive/html/qemu-devel/2017-12/msg00166.html
