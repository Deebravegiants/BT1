# [M] CVE-2020-29486

## Summary
Severity: Medium
Advisory: CVE-2020-29486
CVSS: 6.0 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:C/C:N/I:N/A:H)
Published: 2020-12-15
Source: https://osv.dev/vulnerability/CVE-2020-29486
Type: osv

## Details
An issue was discovered in Xen through 4.14.x. Nodes in xenstore have an ownership. In oxenstored, a owner could give a node away. However, node ownership has quota implications. Any guest can run another guest out of quota, or create an unbounded number of nodes owned by dom0, thus running xenstored out of memory A malicious guest administrator can cause a denial of service against a specific guest or against the whole host. All systems using oxenstored are vulnerable. Building and using oxenstored is the default in the upstream Xen distribution, if the Ocaml compiler is available. Systems using C xenstored are not vulnerable.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/OBLV6L6Q24PPQ2CRFXDX4Q76KU776GKI/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/2C6M6S3CIMEBACH6O7V4H2VDANMO6TVA/
- https://security.gentoo.org/glsa/202107-30
- https://www.debian.org/security/2020/dsa-4812
- https://xenbits.xenproject.org/xsa/advisory-352.html
