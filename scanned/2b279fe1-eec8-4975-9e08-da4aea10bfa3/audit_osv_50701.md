# [H] CVE-2020-29479

## Summary
Severity: High
Advisory: CVE-2020-29479
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2020-12-15
Source: https://osv.dev/vulnerability/CVE-2020-29479
Type: osv

## Details
An issue was discovered in Xen through 4.14.x. In the Ocaml xenstored implementation, the internal representation of the tree has special cases for the root node, because this node has no parent. Unfortunately, permissions were not checked for certain operations on the root node. Unprivileged guests can get and modify permissions, list, and delete the root node. (Deleting the whole xenstore tree is a host-wide denial of service.) Achieving xenstore write access is also possible. All systems using oxenstored are vulnerable. Building and using oxenstored is the default in the upstream Xen distribution, if the Ocaml compiler is available. Systems using C xenstored are not vulnerable.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/2C6M6S3CIMEBACH6O7V4H2VDANMO6TVA/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/OBLV6L6Q24PPQ2CRFXDX4Q76KU776GKI/
- https://security.gentoo.org/glsa/202107-30
- https://www.debian.org/security/2020/dsa-4812
- https://xenbits.xenproject.org/xsa/advisory-353.html
