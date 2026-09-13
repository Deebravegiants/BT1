# [H] CVE-2019-18813

## Summary
Severity: High
Advisory: CVE-2019-18813
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-11-07
Source: https://osv.dev/vulnerability/CVE-2019-18813
Type: osv

## Details
A memory leak in the dwc3_pci_probe() function in drivers/usb/dwc3/dwc3-pci.c in the Linux kernel through 5.3.9 allows attackers to cause a denial of service (memory consumption) by triggering platform_device_add_properties() failures, aka CID-9bbfceea12a8.

## References
- https://security.netapp.com/advisory/ntap-20191205-0001/
- https://usn.ubuntu.com/4225-1/
- https://usn.ubuntu.com/4225-2/
- https://usn.ubuntu.com/4226-1/
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=9bbfceea12a8f145097a27d7c7267af25893c060
