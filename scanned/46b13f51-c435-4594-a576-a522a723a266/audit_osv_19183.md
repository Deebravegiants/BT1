# [M] CVE-2020-8566

## Summary
Severity: Medium
Advisory: CVE-2020-8566
Aliases: GHSA-5x96-j797-5qqw, GO-2024-2754
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2020-12-07
Source: https://osv.dev/vulnerability/CVE-2020-8566
Type: osv

## Details
In Kubernetes clusters using Ceph RBD as a storage provisioner, with logging level of at least 4, Ceph RBD admin secrets can be written to logs. This occurs in kube-controller-manager's logs during provisioning of Ceph RBD persistent claims. This affects < v1.19.3, < v1.18.10, < v1.17.13.

## References
- https://github.com/kubernetes/kubernetes/issues/95624
- https://security.netapp.com/advisory/ntap-20210122-0006/
- https://groups.google.com/g/kubernetes-security-discuss/c/vm-HcrFUOCs/m/36utxAM5CwAJ
