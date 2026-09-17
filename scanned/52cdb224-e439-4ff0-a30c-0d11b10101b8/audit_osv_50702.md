# [H] CVE-2020-29481

## Summary
Severity: High
Advisory: CVE-2020-29481
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2020-12-15
Source: https://osv.dev/vulnerability/CVE-2020-29481
Type: osv

## Details
An issue was discovered in Xen through 4.14.x. Access rights of Xenstore nodes are per domid. Unfortunately, existing granted access rights are not removed when a domain is being destroyed. This means that a new domain created with the same domid will inherit the access rights to Xenstore nodes from the previous domain(s) with the same domid. Because all Xenstore entries of a guest below /local/domain/<domid> are being deleted by Xen tools when a guest is destroyed, only Xenstore entries of other guests still running are affected. For example, a newly created guest domain might be able to read sensitive information that had belonged to a previously existing guest domain. Both Xenstore implementations (C and Ocaml) are vulnerable.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/OBLV6L6Q24PPQ2CRFXDX4Q76KU776GKI/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/2C6M6S3CIMEBACH6O7V4H2VDANMO6TVA/
- https://www.debian.org/security/2020/dsa-4812
- http://www.openwall.com/lists/oss-security/2020/12/16/3
- https://xenbits.xenproject.org/xsa/advisory-322.html
