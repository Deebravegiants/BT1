# [M] CVE-2017-1002100

## Summary
Severity: Medium
Advisory: CVE-2017-1002100
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2017-09-14
Source: https://osv.dev/vulnerability/CVE-2017-1002100
Type: osv

## Details
Default access permissions for Persistent Volumes (PVs) created by the Kubernetes Azure cloud provider in versions 1.6.0 to 1.6.5 are set to "container" which exposes a URI that can be accessed without authentication on the public internet. Access to the URI string requires privileged access to the Kubernetes cluster or authenticated access to the Azure portal.

## References
- https://github.com/kubernetes/kubernetes/issues/47611
- https://groups.google.com/d/msg/kubernetes-security-announce/n3VBg_WJZic/-ddIqKXqAAAJ
