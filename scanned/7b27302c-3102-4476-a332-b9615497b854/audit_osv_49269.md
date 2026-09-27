# [M] CVE-2018-8043

## Summary
Severity: Medium
Advisory: CVE-2018-8043
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-03-10
Source: https://osv.dev/vulnerability/CVE-2018-8043
Type: osv

## Details
The unimac_mdio_probe function in drivers/net/phy/mdio-bcm-unimac.c in the Linux kernel through 4.15.8 does not validate certain resource availability, which allows local users to cause a denial of service (NULL pointer dereference).

## References
- http://www.securitytracker.com/id/1040749
- https://usn.ubuntu.com/3619-1/
- https://usn.ubuntu.com/3619-2/
- https://usn.ubuntu.com/3630-1/
- https://usn.ubuntu.com/3630-2/
- https://usn.ubuntu.com/3632-1/
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=297a6961ffb8ff4dc66c9fbf53b924bd1dda05d5
- https://github.com/torvalds/linux/commit/297a6961ffb8ff4dc66c9fbf53b924bd1dda05d5
