# [H] CVE-2020-27827

## Summary
Severity: High
Advisory: CVE-2020-27827
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-03-18
Source: https://osv.dev/vulnerability/CVE-2020-27827
Type: osv

## Details
A flaw was found in multiple versions of OpenvSwitch. Specially crafted LLDP packets can cause memory to be lost when allocating data to handle specific optional TLVs, potentially causing a denial of service. The highest threat from this vulnerability is to system availability.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/3T5XHPOGIPWCRRPJUE6P3HVC5PTSD5JS/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/JYA4AMJXCNF6UPFG36L2TPPT32C242SP/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/SKQWHG2SZJZSGC7PXVDAEJYBN7ESDR7D/
- https://mail.openvswitch.org/pipermail/ovs-dev/2021-January/379471.html
- https://security.gentoo.org/glsa/202311-16
- https://us-cert.cisa.gov/ics/advisories/icsa-21-194-07
- https://bugzilla.redhat.com/show_bug.cgi?id=1921438
- https://cert-portal.siemens.com/productcert/pdf/ssa-941426.pdf
