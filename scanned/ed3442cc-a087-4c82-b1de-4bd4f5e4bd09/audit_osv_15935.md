# [M] CVE-2019-20808

## Summary
Severity: Medium
Advisory: CVE-2019-20808
CVSS: 6.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2020-12-31
Source: https://osv.dev/vulnerability/CVE-2019-20808
Type: osv

## Details
In QEMU 4.1.0, an out-of-bounds read flaw was found in the ATI VGA implementation. It occurs in the ati_cursor_define() routine while handling MMIO write operations through the ati_mm_write() callback. A malicious guest could abuse this flaw to crash the QEMU process, resulting in a denial of service.

## References
- https://git.qemu.org/?p=qemu.git%3Ba=commit%3Bh=aab0e2a661b2b6bf7915c0aefe807fb60d6d9d13
- https://security.netapp.com/advisory/ntap-20210205-0003/
- https://bugzilla.redhat.com/show_bug.cgi?id=1841136
