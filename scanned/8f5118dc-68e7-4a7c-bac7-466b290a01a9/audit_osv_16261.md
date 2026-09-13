# [M] CVE-2019-3841

## Summary
Severity: Medium
Advisory: CVE-2019-3841
CVSS: 6.8 (CVSS:3.0/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2019-03-25
Source: https://osv.dev/vulnerability/CVE-2019-3841
Type: osv

## Details
Kubevirt/virt-cdi-importer, versions 1.4.0 to 1.5.3 inclusive, were reported to disable TLS certificate validation when importing data into PVCs from container registries. This could enable man-in-the-middle attacks between a container registry and the virt-cdi-component, leading to possible undetected tampering of trusted container image content.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-3841
- https://github.com/kubevirt/containerized-data-importer/issues/678
