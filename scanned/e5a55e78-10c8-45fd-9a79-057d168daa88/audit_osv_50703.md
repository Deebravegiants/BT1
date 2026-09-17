# [M] CVE-2020-29482

## Summary
Severity: Medium
Advisory: CVE-2020-29482
CVSS: 6.0 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:C/C:N/I:N/A:H)
Published: 2020-12-15
Source: https://osv.dev/vulnerability/CVE-2020-29482
Type: osv

## Details
An issue was discovered in Xen through 4.14.x. A guest may access xenstore paths via absolute paths containing a full pathname, or via a relative path, which implicitly includes /local/domain/$DOMID for their own domain id. Management tools must access paths in guests' namespaces, necessarily using absolute paths. oxenstored imposes a pathname limit that is applied solely to the relative or absolute path specified by the client. Therefore, a guest can create paths in its own namespace which are too long for management tools to access. Depending on the toolstack in use, a malicious guest administrator might cause some management tools and debugging operations to fail. For example, a guest administrator can cause "xenstore-ls -r" to fail. However, a guest administrator cannot prevent the host administrator from tearing down the domain. All systems using oxenstored are vulnerable. Building and using oxenstored is the default in the upstream Xen distribution, if the Ocaml compiler is available. Systems using C xenstored are not vulnerable.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/2C6M6S3CIMEBACH6O7V4H2VDANMO6TVA/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/OBLV6L6Q24PPQ2CRFXDX4Q76KU776GKI/
- https://www.debian.org/security/2020/dsa-4812
- https://xenbits.xenproject.org/xsa/advisory-323.html
