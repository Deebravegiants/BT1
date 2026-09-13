# [H] CVE-2024-31143

## Summary
Severity: High
Advisory: CVE-2024-31143
CVSS: 7.5 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-07-18
Source: https://osv.dev/vulnerability/CVE-2024-31143
Type: osv

## Details
An optional feature of PCI MSI called "Multiple Message" allows a
device to use multiple consecutive interrupt vectors.  Unlike for MSI-X,
the setting up of these consecutive vectors needs to happen all in one
go.  In this handling an error path could be taken in different
situations, with or without a particular lock held.  This error path
wrongly releases the lock even when it is not currently held.

## References
- http://www.openwall.com/lists/oss-security/2024/07/16/3
- http://xenbits.xen.org/xsa/advisory-458.html
- https://xenbits.xenproject.org/xsa/advisory-458.html
