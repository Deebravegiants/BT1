# [M] CVE-2016-5242

## Summary
Severity: Medium
Advisory: CVE-2016-5242
CVSS: 5.6 (CVSS:3.0/AV:L/AC:H/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2016-06-07
Source: https://osv.dev/vulnerability/CVE-2016-5242
Type: osv

## Details
The p2m_teardown function in arch/arm/p2m.c in Xen 4.4.x through 4.6.x allows local guest OS users with access to the driver domain to cause a denial of service (NULL pointer dereference and host OS crash) by creating concurrent domains and holding references to them, related to VMID exhaustion.

## References
- http://www.securityfocus.com/bid/91015
- http://www.securitytracker.com/id/1036035
- http://www.debian.org/security/2016/dsa-3633
- http://xenbits.xen.org/xsa/advisory-181.html
