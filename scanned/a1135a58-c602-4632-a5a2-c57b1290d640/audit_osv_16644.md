# [M] CVE-2019-8396

## Summary
Severity: Medium
Advisory: CVE-2019-8396
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-02-17
Source: https://osv.dev/vulnerability/CVE-2019-8396
Type: osv

## Details
A buffer overflow in H5O__layout_encode in H5Olayout.c in the HDF HDF5 through 1.10.4 library allows attackers to cause a denial of service via a crafted HDF5 file. This issue was triggered while repacking an HDF5 file, aka "Invalid write of size 2."

## References
- https://github.com/magicSwordsMan/PAAFS/tree/master/vul4
