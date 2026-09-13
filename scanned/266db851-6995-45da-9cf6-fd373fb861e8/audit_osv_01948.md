# [M] ALPINE-CVE-2020-29482

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2020-29482
Ecosystem: Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.0 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:C/C:N/I:N/A:H)
Published: 2020-12-15
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-29482
Type: osv

## Affected
- Alpine:v3.11: `xen` — affected >=0 <4.13.2-r3
- Alpine:v3.12: `xen` — affected >=0 <4.13.2-r3
- Alpine:v3.13: `xen` — affected >=0 <4.14.1-r0
- Alpine:v3.14: `xen` — affected >=0 <4.14.1-r0
- Alpine:v3.15: `xen` — affected >=0 <4.14.1-r0
- Alpine:v3.16: `xen` — affected >=0 <4.14.1-r0
- Alpine:v3.17: `xen` — affected >=0 <4.14.1-r0
- Alpine:v3.18: `xen` — affected >=0 <4.14.1-r0
- Alpine:v3.19: `xen` — affected >=0 <4.14.1-r0
- Alpine:v3.20: `xen` — affected >=0 <4.14.1-r0
- Alpine:v3.21: `xen` — affected >=0 <4.14.1-r0
- Alpine:v3.22: `xen` — affected >=0 <4.14.1-r0
- Alpine:v3.23: `xen` — affected >=0 <4.14.1-r0
- Alpine:v3.24: `xen` — affected >=0 <4.14.1-r0

## Details
An issue was discovered in Xen through 4.14.x. A guest may access xenstore paths via absolute paths containing a full pathname, or via a relative path, which implicitly includes /local/domain/$DOMID for their own domain id. Management tools must access paths in guests' namespaces, necessarily using absolute paths. oxenstored imposes a pathname limit that is applied solely to the relative or absolute path specified by the client. Therefore, a guest can create paths in its own namespace which are too long for management tools to access. Depending on the toolstack in use, a malicious guest administrator might cause some management tools and debugging operations to fail. For example, a guest administrator can cause "xenstore-ls -r" to fail. However, a guest administrator cannot prevent the host administrator from tearing down the domain. All systems using oxenstored are vulnerable. Building and using oxenstored is the default in the upstream Xen distribution, if the Ocaml compiler is available. Systems using C xenstored are not vulnerable.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-29482
