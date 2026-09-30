# [M] CVE-2021-3557

## Summary
Severity: Medium
Advisory: CVE-2021-3557
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-02-16
Source: https://osv.dev/vulnerability/CVE-2021-3557
Type: osv

## Details
A flaw was found in argocd. Any unprivileged user is able to deploy argocd in their namespace and with the created ServiceAccount argocd-argocd-server, the unprivileged user is able to read all resources of the cluster including all secrets which might enable privilege escalations. The highest threat from this vulnerability is to data confidentiality.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1961929
