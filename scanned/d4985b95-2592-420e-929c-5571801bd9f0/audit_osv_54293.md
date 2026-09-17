# [M] CVE-2023-46839

## Summary
Severity: Medium
Advisory: CVE-2023-46839
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2024-03-20
Source: https://osv.dev/vulnerability/CVE-2023-46839
Type: osv

## Details
PCI devices can make use of a functionality called phantom functions,
that when enabled allows the device to generate requests using the IDs
of functions that are otherwise unpopulated.  This allows a device to
extend the number of outstanding requests.

Such phantom functions need an IOMMU context setup, but failure to
setup the context is not fatal when the device is assigned.  Not
failing device assignment when such failure happens can lead to the
primary device being assigned to a guest, while some of the phantom
functions are assigned to a different domain.

## References
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/XLL6SQ6IKFYXLYWITYZCRV5IBRK5G35R/
- https://xenbits.xenproject.org/xsa/advisory-449.html
- http://xenbits.xen.org/xsa/advisory-449.html
