# [M] CVE-2023-2088

## Summary
Severity: Medium
Advisory: CVE-2023-2088
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-05-12
Source: https://osv.dev/vulnerability/CVE-2023-2088
Type: osv

## Details
A flaw was found in OpenStack due to an inconsistency between Cinder and Nova. This issue can be triggered intentionally or by accident. A remote, authenticated attacker could exploit this vulnerability by detaching one of their volumes from Cinder. The highest impact is to confidentiality.

## References
- https://bugs.launchpad.net/bugs/2004555
- https://security.openstack.org/ossa/OSSA-2023-003.html
